

## When a list of translations is passed, It throws out android strings.xml files
class AndroidStringGenerator:

    def __init(self, translations):
        self.translations = translations

        def create_file(lines, country_id):
            directory = ROOT_FOLDER + "/values-" + country_id
            create_folders(directory)
            to_xml = open(directory + '/strings.xml', 'w')
            to_xml.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')
            for line in lines:
                string = get_xml_string(line)
                if string:
                    to_xml.write(string)
            to_xml.write('\n</resources>')
            to_xml.close()

        def create_folders(directory):
            if not os.path.exists(directory):
                os.makedirs(directory)

        def get_xml_string(line):
            if line:
                try:
                    old_key, new_key = line.split("=")

                    ## replace the values with ios specific stuff to android xml
                    new_key = new_key.split("\n")[0]
                    new_key = new_key.replace('"', '').split(';')[0]
                    new_key = new_key.replace("&", "&amp;")
                    new_key = new_key.replace("%@", "%s")

                    ## replace / in keys with _ for xml
                    old_key = old_key.replace("/", "_")
                    return '\t<string name=' + old_key.strip() + '>' + new_key.strip() + '</string>' + '\n'
                except Exception, e:
                    return None
