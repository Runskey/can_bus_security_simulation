from glob_def import *

class SimpleMsg:
    can_id = 0
    desc = ""
    byte_len = 0
    bit_start_pos = 0
    bit_num = 0
    scale = 0.0
    offset = 0.0
    unit = ""

    def __init__(self, can_id, byte_len, bit_start_pos, bit_num, scale, offset, desc = "", unit=""):
        self.can_id = can_id
        self.byte_len = byte_len
        self.bit_start_pos = bit_start_pos
        self.bit_num = bit_num
        self.scale = scale
        self.offset = offset
        self.desc = desc
        self.unit = unit

DBC_DATABASE_TOYOTA_PRIUS = { \
    0x00b4 : SimpleMsg(can_id=0xb4, byte_len=8,           \
                       bit_start_pos=47, bit_num=16,      \
                       scale=0.01, offset=0.0,            \
                       desc="Current speed of the automobile", unit="kmph"), \
    0x01c4:  SimpleMsg(can_id=0x01c4, byte_len=8,         \
                       bit_start_pos=15, bit_num=16,      \
                       scale=1.0, offset=-400.0,          \
                       desc="ICE RPM", unit=""),          \
    0x0224:  SimpleMsg(can_id=0x0224, byte_len=8,         \
                       bit_start_pos=47, bit_num=16,      \
                       scale=0.01, offset=0.0,            \
                       desc="Brake pedal position sensor", unit=""), \
    0x0230:  SimpleMsg(can_id=0x0230, byte_len=7,         \
                       bit_start_pos=31, bit_num=8,       \
                       scale=1.0, offset=0.0,             \
                       desc="Brake sensor", unit=""),     \
    0x0245:  SimpleMsg(can_id=0x0245, byte_len=5,         \
                       bit_start_pos=15, bit_num=16,      \
                       scale=0.0062, offset=0,            \
                       desc="Acceleration pedal position", unit="mph") \
}

class DbcMsgConvertor:
    vehicle_model = "unknown"
    dbc_database = None
    def __init__(self, model):
        self.vehicle_model = model
        database_name = "DATABASE_" + str(model).upper()
        if database_name in dir():
            self.dbc_database = eval(database_name)
        else:
            print("DBC database %s doesn't exist!" % database_name)
            # raise an error

    def simple_msg_encode(self, id, value):
        msg = self.dbc_database[id]
        # calculate pre- and post- zero pending string
        data_prezero = '00' * ((msg.bit_start_pos-msg.bit_num) >> 3 + 1)
        data_postzero = '00' * (msg.byte_len-1-msg.bit_start_pos>>3)
        # convert value to hex string
        data_fmt = '0'+str(msg.bit_num>>2)+'x'
        data_value = format(int((value-msg.offset)/msg.scale), data_fmt)
        data = data_prezero + data_value + data_postzero
        return data

    def simple_msg_decode(self, id, data):
        msg = self.dbc_database[id]
        byte_end = (msg.bit_start_pos>>3)*2 + 2
        byte_start = (msg.bit_start_pos-msg.bit_num)>>3 * 2 + 2
        value = int(data[byte_start:byte_end], 16)*msg.scale+msg.offset
        return value