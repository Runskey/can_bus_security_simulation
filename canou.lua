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

local f_canid = ProtoField.uint32("canou.canid", "CAN Message Name", base.DEC, canid_set)
local f_canlen = ProtoField.uint8("canou.msglen", "Length of Byte", base.DEC)
local f_canval = ProtoField.uint32("canou.msgval", "Value", base.DEC)
local f_canmsg = ProtoField.string("canou.text", "Addi. Info")

CANoU.fields = { f_canid, f_canlen, f_canval, f_canmsg }

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
                local value_byte_num = (decoder['bit_start'] + decoder['bit_num']) / 8
                local bit_shift = 8 - (decoder['bit_start'] + decoder['bit_num']) % 8

                for i=0,value_byte_num do
                        local newbyte = buf(16+i,1):uint()
                        -- to remove prefix for first byte
                        --[[
                        if i == 0
                        then
                                local bitmask = 2 ^ (8 - decoder['bit_start'] % 8)
                                newbyte = newbyte & bitmask
                        end
                        value = (value * 256) + newbyte
                        --]]
                end
                value = value / (2^bit_shift)
                value = value * decoder['scale']+decoder['offset']
        end

        subtree:add(f_canval, value)
end

-- register this dissector
local udp_encap_table = DissectorTable.get("udp.port")
udp_encap_table:add(PORT, CANoU)