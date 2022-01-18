DAB_CHANNELS = {'5A': 174928, '5B': 176640, '5C': 178352, '5D': 180064, '6A': 181936,
                '6B': 183648, '6C': 185360, '6D': 187072, '7A': 188928, '7B': 190640,
                '7C': 192352, '7D': 194064, '8A': 195936, '8B': 197648, '8C': 199360,
                '8D': 201072, '9A': 202928, '9B': 204640, '9C': 206352, '9D': 208064,
                '10A': 209936, '10B': 211648, '10C': 213360, '10D': 215072, '11A': 216928,
                '11B': 218640, '11C': 220352, '11D': 222064, '12A': 223936, '12B': 225648,
                '12C': 227360, '12D': 229072, '13A': 230784, '13B': 232496, '13C': 234208,
                '13D': 235776, '13E': 237448, '13F': 239200}

UK_CHANNELS = ['10A', '10B', '10C', '10D', '11A',
               '11B', '11C', '11D', '12A', '12B', '12C', '12D']

PTY_TYPES = ["", "News", "Current affairs", "Information", "Sport", "Education", "Drama",
             "Culture", "Science", "Varied", "Popmusic", "Rockmusic", "Easy listening", "Light classical",
             "Serious classical", "Other music", "Weather", "Finance", "Children’s programmes",
             "Social affairs", "Religion", "Phone-in", "Travel", "Leisure", "Jazz music", "Country music",
             "National music", "Oldies music", "Folk music", "Documentary", "Alarm test", "Alarm"]

# SI468x Commands
POWER_ON = 0x01
RD_REPLY = 0x00
SET_PROPERTY = 0x13
GET_PROPERTY = 0x14
GET_AGC_STATUS = 0x17

FM_TUNE_FREQ = 0x30
FM_SEEK_START = 0x31
FM_RSQ_STATUS = 0x32
FM_ACF_STATUS = 0x33
FM_RDS_STATUS = 0x34
FM_RDS_BLOCKCOUNT = 0x35

GET_DIGITAL_SERVICE_LIST = 0x80  # Gets a service list of the ensemble.
START_DIGITAL_SERVICE = 0x81  # Starts an audio or data service.
STOP_DIGITAL_SERVICE = 0x82  # Stops an audio or data service.
# Gets a block of data associated with one of the enabled data components of a digital services.
GET_DIGITAL_SERVICE_DATA = 0x84
# Tunes the DAB Receiver to tune to a frequency between 168.16 and 239.20 MHz defined by the frequency table through DAB_SET_FREQ_LIST.
DAB_TUNE_FREQ = 0xB0
# Returns status information about the digital radio and ensemble.
DAB_DIGRAD_STATUS = 0xB2
# Gets information about the various events related to the DAB radio.
DAB_GET_EVENT_STATUS = 0xB3
DAB_GET_ENSEMBLE_INFO = 0xB4  # Gets information about the current ensemble
# gets the announcement support information.
DAB_GET_ANNOUNCEMENT_SUPPORT_INFO = 0xB5
# gets announcement information from the announcement queue
DAB_GET_ANNOUNCEMENT_INFO = 0xB6
# Provides service linking (FIG 0/6) information for the passed in service ID.
DAB_GET_SERVICE_LINKING_INFO = 0xB7
# Sets the DAB frequency table. The frequencies are in units of kHz.
DAB_SET_FREQ_LIST = 0xB8
DAB_GET_FREQ_LIST = 0xB9  # Returns the frequency table
# Gets information about components within the ensemble if available.
DAB_GET_COMPONENT_INFO = 0xBB
# Gets the ensemble time adjusted for the local time offset or the UTC.
DAB_GET_TIME = 0xBC
DAB_GET_AUDIO_INFO = 0xBD  # Gets audio service info
DAB_GET_SUBCHAN_INFO = 0xBE  # Gets sub-channel info
DAB_GET_FREQ_INFO = 0xBF  # Gets ensemble freq info
DAB_GET_SERVICE_INFO = 0xC0  # Gets information about a service.
# Provides other ensemble (OE) services (FIG 0/24) information for the passed in service ID.
DAB_GET_OE_SERVICES_INFO = 0xC1
# Returns status information about automatically controlled features.
DAB_ACF_STATUS = 0xC2


# Properties
INT_CTL_ENABLE = 0x0000
