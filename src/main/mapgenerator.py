class MapGenerator:
    def __init__(self):
        self.name = None
    
    def fromXml(xml):
        self = MapGenerator()
        self.loadXml(xml)
        return self
    
    def loadXml(self, xml):
        # TODO: load
        self.name = xml.attrib['name']
    
    def generate(self, tMap):
        # TODO: work
        tMap.getContent(2, 2, 'ground').attrib['char'] = '?'
