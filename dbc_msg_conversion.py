from glob_def import CarEvent


class SimpleMsg:
    can_id = 0
    desc = ""
    byte_len = 0
    bit_start_pos = 0
    bit_num = 0
    scale = 0.0
    offset = 0.0
    unit = ""

    def __init__(self, can_id, byte_len, bit_start_pos, bit_num,
                 scale, offset, desc="", unit=""):
        self.can_id = can_id
        self.byte_len = byte_len
        self.bit_start_pos = bit_start_pos
        self.bit_num = bit_num
        self.scale = scale
        self.offset = offset
        self.desc = desc
        self.unit = unit


DBC_DATABASE_TOYOTA_PRIUS = {
    CarEvent.CAR_EVENT_GAS_ACC_VIA_ICE:
    SimpleMsg(can_id=0x37, byte_len=7,
              bit_start_pos=0, bit_num=40,
              scale=1.0, offset=0.0,
              desc="Acceleration via ICE", unit=""),
    CarEvent.CAR_EVENT_QUERY_SPEED:
    SimpleMsg(can_id=0xb4, byte_len=8,
              bit_start_pos=47, bit_num=16,
              scale=0.01, offset=0.0,
              desc="Current speed of the automobile", unit="kmph"),
    CarEvent.CAR_EVENT_QUERY_RPM:
    SimpleMsg(can_id=0x01c4, byte_len=8,
              bit_start_pos=15, bit_num=16,
              scale=1.0, offset=-400.0,
              desc="ICE RPM", unit=""),
    CarEvent.CAR_EVENT_QUERY_TORQUE:
    SimpleMsg(can_id=0x24, byte_len=8,
              bit_start_pos=15, bit_num=16,
              scale=1.0, offset=0.0,
              desc="ICE Torque", unit=""),
    CarEvent.CAR_EVENT_BRAKE_PEDAL:
    SimpleMsg(can_id=0x0224, byte_len=8,
              bit_start_pos=47, bit_num=16,
              scale=0.01, offset=0.0,
              desc="Brake pedal position sensor", unit=""),
    CarEvent.CAR_EVENT_STEERING_WHEEL_ANGLE:
    SimpleMsg(can_id=0x25, byte_len=8,
              bit_start_pos=3, bit_num=12,
              scale=1.5, offset=0.0,
              desc="Steer wheel angle", unit="deg"),
    CarEvent.CAR_EVENT_BROADCAST_GEAR_STATUS:
    SimpleMsg(can_id=0x127, byte_len=8,
              bit_start_pos=0, bit_num=64,
              scale=1.0, offset=0.0,
              desc="Broadcast gear status", unit=""),
    CarEvent.CAR_EVENT_BRAKE_SENSOR:
    SimpleMsg(can_id=0x0230, byte_len=7,
              bit_start_pos=31, bit_num=8,
              scale=1.0, offset=0.0,
              desc="Brake sensor", unit=""),
    CarEvent.CAR_EVENT_GAS_PEDAL:
    SimpleMsg(can_id=0x0245, byte_len=5,
              bit_start_pos=15, bit_num=16,
              scale=0.0062, offset=0,
              desc="Acceleration pedal position", unit="mph"),
    CarEvent.CAR_EVENT_PCS_PRECOLLISION:
    SimpleMsg(can_id=0x0283, byte_len=7,
              bit_start_pos=16, bit_num=24,
              scale=1.0, offset=0.0,
              desc="Pre-collision action", unit=""),
    CarEvent.CAR_EVENT_BUS_DIAG:
    SimpleMsg(can_id=0x7df, byte_len=8,
              bit_start_pos=15, bit_num=16,
              scale=1.0, offset=0,
              desc="Universal diagnostic message", unit="")
}


class DbcMsgConvertor:
    vehicle_model = "unknown"
    dbc_database = None

    def __init__(self, model):
        self.vehicle_model = model
        database_name = "DBC_DATABASE_" + str(model).upper()
        try:
            self.dbc_database = eval(database_name)
        except NameError:
            print("DBC database %s doesn't exist!" % database_name)
            # raise an error
            assert(False)

    def simple_msg_encode(self, id, value):
        # convert value to pre-defined dbc format
        # return value is string in hex represenation

        if id in self.dbc_database:
            msg = self.dbc_database[id]
        else:
            msg = SimpleMsg(can_id=id, byte_len=8, bit_start_pos=16,
                            bit_num=4, scale=1.0, offset=0.0)

        binstr = '0' * msg.byte_len * 8

        # convert value to binary
        binfmt = '0'+str(msg.bit_num)+'b'
        data_value = format(int((value-msg.offset)/msg.scale), binfmt)
        assert(len(data_value) <= msg.bit_num)

        # combine binary string
        postzeronum = msg.byte_len*8-msg.bit_start_pos-msg.bit_num
        binstr = '0'*msg.bit_start_pos + data_value + '0'*postzeronum

        # convert binary to hex
        hexfmt = '0'+str(msg.byte_len*2)+'x'
        hexstr = format(int(binstr, 2), hexfmt)

        return hexstr

    def simple_msg_decode(self, id, data):
        if id in self.dbc_database:
            msg = self.dbc_database[id]
        else:
            msg = SimpleMsg(can_id=id, byte_len=8, bit_start_pos=16,
                            bit_num=4, scale=1.0, offset=0.0)

        bin_str = format(int(data, 16), '064b')
        bin_value = bin_str[msg.bit_start_pos:msg.bit_start_pos+msg.bit_num]
        value = int(bin_value, 2)*msg.scale+msg.offset

        return value

    def get_msg_length_in_byte(self, id):
        if id in self.dbc_database:
            msg = self.dbc_database[id]
            return msg.byte_len
        else:
            return 0

    def get_msg_can_id(self, id):
        if id in self.dbc_database:
            msg = self.dbc_database[id]
            return msg.can_id
        else:
            return 0xffff

    def get_event_id_by_can_id(self, can_id):
        for i in self.dbc_database:
            msg = self.dbc_database[i]
            if msg.can_id == can_id:
                return i
        return CarEvent.CAR_EVENT_UNKNOWN
