import urllib2
import xml.etree.ElementTree as ET
from errors import handle
from prettyprint import *
import pick

CMIP5_FACET_LISTING = \
    'https://esgf-node.llnl.gov/esg-search/search?project=CMIP5&facets=*&limit=0'

CMIP5_FACET_QUERY = \
    'https://esgf-node.llnl.gov/esg-search/search?project=CMIP5&facets=%s&limit=0'

CMIP5_FILE_PREFIX = \
    'https://esgf-node.llnl.gov/esg-search/search?type=File&project=CMIP5'

REQUEST_LIMIT = 1000

class Order:
    
    def __init__(self):
        pass

    def fetch_facets(self):

        # Create facet list
        file = urllib2.urlopen(CMIP5_FACET_LISTING)
        data = file.read()
        file.close()
        tree = ET.fromstring(data)
        try:
            facet_array = \
                tree.find('lst').find('lst').find('arr')
            assert facet_array.get('name') == 'facet.field'
            facet_names = [ff.text for ff in facet_array.findall('str')]
        except:
            handle(AttributeError('Could not parse facet listing'))

        # Create list of facets with fields
        self.facets = dict()
        for facet in facet_names:
            ppinfo('Processing facet %s' % facet)
            file = urllib2.urlopen(CMIP5_FACET_QUERY % facet)
            data = file.read()
            file.close()
            tree = ET.fromstring(data)
            try:
                sections = iter(tree.findall('lst'))
                facet_counts = next(sections)
                while facet_counts.get('name') != 'facet_counts':
                    facet_counts = next(sections)
                sections = iter(facet_counts.findall('lst'))
                facet_fields = next(sections)
                while facet_fields.get('name') != 'facet_fields':
                    facet_fields = next(sections)
                facet_element = facet_fields.find('lst')
                assert(facet_element.get('name') == facet)
                fields = facet_element.findall('int')
                names = [ff.get('name') for ff in fields]
                values = [int(ff.text) for ff in fields]
                if len(names) > 0:
                    self.facets[facet] = dict(zip(names, values))
            except:
                handle(AttributeError('Could not parse options for facet %s' % facet))

    def set_filters(self):
        if not hasattr(self, 'facets'):
            pperror('Facet information not present')
            ppinfo('Run Order.fetch_facets() to retrieve facet listing')
            return
        
        self.filters = dict()
        finished = False
        
        # Select filters
        while not finished:
            title = 'Choose a facet or finish'
            options = self.facets.keys()
            options.sort()
            options.insert(0, '[FINISH]')
            option, index = pick.pick(options, title)
            if option == '[FINISH]':
                finished = True
            else:
                title = 'Choose filters (SPACE to select, ENTER to continue)'
                options = self.facets[option].keys()
                options.sort()
                selected = pick.pick(options, title, multi_select = True, min_selection_count = 1)
                selected = [ss[0] for ss in selected]
                self.filters[option] = selected
        
        # Save to file (optional)
        option, index = pick.pick(['Yes', 'No'], 'Create filter file?')
        if index == 0:
            self.write_filter_file()

    def write_filter_file(self):
        if not hasattr(self, 'filters'):
            pperror('Filters are not set')
            ppinfo('Run Object.set_filters() to set filters')
            return
        fname = ppinput('File name: ')
        with open('%s.filter' % fname, 'w') as fid:
            for ff in self.filters.keys():
                fid.write('%s:\n' % ff)
                for sel in self.filters[ff]:
                    fid.write('    %s\n' % sel)
                fid.write('\n')

    def read_filter_file(self, fname):
        self.filters = dict()
        ckey = None
        csel = list()
        with open(fname, 'r') as fid:
            for line in fid:
                if line.strip().endswith(':'):
                    if ckey is not None and len(csel) > 0:
                        self.filters[ckey] = csel
                    ckey = line.strip()[:-1]
                    csel = list()
                elif len(line.strip()) > 0:
                    csel.append(line.strip())
            if ckey is not None and len(csel) > 0:
                self.filters[ckey] = csel
    
    def submit_order(self):
        self.create_url()
        # TODO: set limit and increase offset to move through all files, downloading as you go
         
    def create_url(self):
        if not hasattr(self, 'filters'):
            pperror('Filters are not set')
            ppinfo('Run Object.set_filters() to set filters')
            return
        self.url = CMIP5_FILE_PREFIX
        for ff in self.filters.keys():
            for sel in self.filters[ff]:
                self.url += '&%s=%s' % (ff, sel)
        self.url += '&limit=%d' % REQUEST_LIMIT

