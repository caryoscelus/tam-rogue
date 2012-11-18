class MapGenerator:
    def __init__(self):
        self.name = None
    
    def fromXml(xml):
        self = MapGenerator()
        self.loadXml(xml)
        return self
    
    def loadXml(self, xml):
        self.name = xml.attrib['name']
