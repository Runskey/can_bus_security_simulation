-- @brief CAN-over-UDP Protocol dissector plugin
-- @author 
-- @date 2018.07.12

-- create a new dissector
local NAME = "CANoU"
local PORT = 3248
local CANoU = Proto(NAME, "CAN-over-UDP Protocol")


local canid_set = {
        [0x37] = "Acceleration via ICE",
        [0xb4] = "Current speed of the automobile",
        [0x1c4] = "ICE RPM",
        [0x24] = "ICE Torque",
        [0x224] = "Brake pedal position sensor",
        [0x25] = "Steer wheel angle",
        [0x230] = "Brake sensor",
        [0x245] = "Gas pedal position",
        [0x283] = "Pre-collision action",
        [0x7df] = "Universal diagnostic message"
}
local DBC_DATABASE = {
        [0x0037] = {['bytelen']=7, ['bit_start']= 0, ['bit_num']=40, ['scale']=1.0, ['offset']=0.0},
        [0x00b4] = {['bytelen']=8, ['bit_start']=47, ['bit_num']=16, ['scale']=0.01, ['offset']=0.0},
        [0x0104] = {['bytelen']=8, ['bit_start']=15, ['bit_num']=16, ['scale']=1.0, ['offset']=-400},
        [0x0024] = {['bytelen']=8, ['bit_start']=15, ['bit_num']=16, ['scale']=1.0, ['offset']=0.0},
        [0x0224] = {['bytelen']=8, ['bit_start']=47, ['bit_num']=16, ['scale']=0.01, ['offset']=0.0},
        [0x0025] = {['bytelen']=8, ['bit_start']=3, ['bit_num']=12, ['scale']=1.5, ['offset']=0.0},
        [0x0230] = {['bytelen']=7, ['bit_start']=31, ['bit_num']=8, ['scale']=1.0, ['offset']=0.0},
        [0x0245] = {['bytelen']=5, ['bit_start']=15, ['bit_num']=16, ['scale']=0.0062, ['offset']=0.0},
        [0x0283] = {['bytelen']=7, ['bit_start']=16, ['bit_num']=24, ['scale']=1.0, ['offset']=0.0},
        [0x07df] = {['bytelen']=8, ['bit_start']=15, ['bit_num']=16, ['scale']=1.0, ['offset']=0.0}
}

--[[
local vs_protos = {
        [2] = "mtp2",
        [3] = "mtp3",
        [4] = "alcap",
        [5] = "h248",
        [6] = "ranap",
        [7] = "rnsap",
        [8] = "nbap"
}

local f_proto = ProtoField.uint8("multi.protocol", "Protocol", base.DEC, vs_protos)
local f_dir = ProtoField.uint8("multi.direction", "Direction", base.DEC, { [1] = "incoming", [0] = "outgoing"})
local f_text = ProtoField.string("multi.text", "Text")
--]]

local f_canid = ProtoField.uint32("canou.canid", "CAN ID", base.DEC, canid_set)
local f_canlen = ProtoField.uint8("canou.msglen", "Msg Len", base.DEC)
local f_canval = ProtoField.uint32("canou.msgval", "Msg Value", base.DEC)
local f_canmsg = ProtoField.string("canou.text", "Msg Info")

--CANoU.fields = { f_proto, f_dir, f_text }
CANoU.fields = { f_canid, f_canlen, f_canval, f_canmsg }

--[[
local data_dis = Dissector.get("data")
local protos = {
        [2] = Dissector.get("mtp2"),
        [3] = Dissector.get("mtp3"),
        [4] = Dissector.get("alcap"),
        [5] = Dissector.get("h248"),
        [6] = Dissector.get("ranap"),
        [7] = Dissector.get("rnsap"),
        [8] = Dissector.get("nbap"),
        [9] = Dissector.get("rrc"),
        [10] = DissectorTable.get("sctp.ppi"):get_dissector(3), -- m3ua
        [11] = DissectorTable.get("ip.proto"):get_dissector(132), -- sctp
}
--]]


-- dissect packet
function CANoU.dissector(buf, pkt, tree)

        local subtree = tree:add(CANoU, buf(0,24))
        subtree:add_le(f_canid, buf(8,4))
        subtree:add(f_canlen, buf(15,1))
--        subtree:add(f_canval, buf(16,8))

        -- extract CAN ID
        local canid = buf(8,4):le_uint()
        local msg_string = canid_set[canid]
        if msg_string == nil then
                subtree:add(f_canmsg, "unknown message type")
        else
                subtree:add(f_canmsg, msg_string)
        end

        -- decode the value carried in CAN message
        local value = 0
        local decoder = DBC_DATABASE[canid]
        if decoder == nil
        then
                value = canid
        else
                local bit_start = decoder['bit_start']
                local bit_num = decoder['bit_num']
                local value_byte_num = (bit_start+bit_num) / 8
                local bit_shift = 8 - (bit_start+bit_num) % 8

                for i=0,value_byte_num do
                        local newbyte = buf(16+i,1):uint()
                        value = (value * 256) + newbyte
                end
                value = value / (2^bit_shift)
                value = value * decoder['scale']+decoder['offset']
        end

        subtree:add(f_canval, value)

        --[[
        local subtree = tree:add(CANoU, buf(0,2))
        subtree:add(f_proto, buf(0,1))
        subtree:add(f_dir, buf(1,1))

        local proto_id = buf(0,1):uint()

        local dissector = protos[proto_id]

        if dissector ~= nil then
                -- Dissector was found, invoke subdissector with a new Tvb,
                -- created from the current buffer (skipping first two bytes).
                dissector:call(buf(2):tvb(), pkt, tree)
        elseif proto_id < 2 then
                subtree:add(f_text, buf(2))
                -- pkt.cols.info:set(buf(2, buf:len() - 3):string())
        else
                -- fallback dissector that just shows the raw data.
                data_dis:call(buf(2):tvb(), pkt, tree)
        end
        --]]

end

-- register this dissector
--local wtap_encap_table = DissectorTable.get("wtap_encap")
local udp_encap_table = DissectorTable.get("udp.port")

--wtap_encap_table:add(wtap.USER15, CANoU)
--wtap_encap_table:add(wtap.USER12, CANoU)
udp_encap_table:add(PORT, CANoU)