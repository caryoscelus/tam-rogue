import entity

def loadXMLLayers(xml):
    order = []
    content = {}
    emptyContent = {}
    
    for layer in xml:
        if layer.tag == 'layer':
            try:
                name = layer.attrib['name']
                if layer.attrib['type'] == 'object':
                    try:
                        layerContent = entity.Entity.fromXml(layer[0])
                    except IndexError:
                        layerContent = None
                    emptyLayer = None
                elif layer.attrib['type'] == 'list':
                    layerContent = [entity.Entity.fromXml(e) for e in layer]
                    emptyLayer = []
                else:
                    logging.warning('unknown xml tile layer type')
            except KeyError:
                raise XmlLoadError(layer)
            order.append(name)
            content[name] = layerContent
            emptyContent[name] = emptyLayer
        else:
            logging.warning('unknown xml node type')
    
    return order, content, emptyContent
