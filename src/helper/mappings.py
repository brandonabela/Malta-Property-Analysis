import pandas as pd


class Mappings(object):
    @staticmethod
    def town_mapping():
        data = [
            ['Gozo Sannat', 'Gozo - Sannat']
        ]

        return pd.DataFrame(data, columns=['From', 'To'])

    @staticmethod
    def region_mapping():
        data = [
            ['Central', 'Attard'],
            ['Central', 'Balzan'],
            ['South Eastern', 'Birgu'],
            ['Central', 'Birkirkara'],
            ['Southern', 'Birzebbuga'],
            ['Northern', 'Bugibba'],
            ['South Eastern', 'Cospicua'],
            ['South Eastern', 'Fgura'],
            ['South Eastern', 'Floriana'],
            ['Gozo', 'Gozo - Citadel'],
            ['Gozo', 'Gozo - Fontana'],
            ['Gozo', 'Gozo - Ghajnsielem'],
            ['Gozo', 'Gozo - Gharb'],
            ['Gozo', 'Gozo - Għasri'],
            ['Gozo', 'Gozo - Kerċem'],
            ['Gozo', 'Gozo - Marsalforn'],
            ['Gozo', 'Gozo - Mdina'],
            ['Gozo', 'Gozo - Mgarr'],
            ['Gozo', 'Gozo - Munxar'],
            ['Gozo', 'Gozo - Nadur'],
            ['Gozo', 'Gozo - Qala'],
            ['Gozo', 'Gozo - San Lawrenz'],
            ['Gozo', 'Gozo - Sannat'],
            ['Gozo', 'Gozo - Victoria'],
            ['Gozo', 'Gozo - Xaghra'],
            ['Gozo', 'Gozo - Xewkija'],
            ['Gozo', 'Gozo - Xlendi'],
            ['Gozo', 'Gozo - Żebbuġ'],
            ['Southern', 'Gudja'],
            ['Central', 'Gzira'],
            ['Northern', 'Had-Dingli'],
            ['Northern', 'Hal Gharghur'],
            ['Southern', 'Hamrun'],
            ['South Eastern', 'Haz-Zabbar'],
            ['Southern', 'Haz-Zebbug'],
            ['South Eastern', 'Kalkara'],
            ['Central', 'Lija'],
            ['Southern', 'Marsaskala'],
            ['Southern', 'Marsaxlokk'],
            ['Northern', 'Mdina'],
            ['Northern', 'Mellieha'],
            ['Northern', 'Mgarr'],
            ['Northern', 'Mosta'],
            ['Central', 'Msida'],
            ['Northern', 'Naxxar'],
            ['Northern', 'Paceville'],
            ['Northern', 'Pembroke'],
            ['Northern', 'Qawra'],
            ['Southern', 'Qormi'],
            ['Southern', 'Qrendi'],
            ['Northern', 'Rabat'],
            ['Central', 'Saint Julian\'s'],
            ['Northern', 'Saint Paul\'s Bay'],
            ['Central', 'San Gwann'],
            ['South Eastern', 'Senglea'],
            ['Southern', 'Siggiewi'],
            ['Central', 'Sliema'],
            ['Northern', 'Swieqi'],
            ['Central', 'Ta\' Xbiex'],
            ['South Eastern', 'Tarxien'],
            ['South Eastern', 'Valletta'],
            ['South Eastern', 'Zejtun'],
            ['Southern', 'Zurrieq']
        ]

        return pd.DataFrame(data, columns=['Province', 'Town'])
