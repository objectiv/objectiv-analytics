# all data below is generated dummy data
TEST_DATA_JSON_REAL = [
    [1,
     '[{"_type": "ApplicationContext", "id": "rod-web-demo"}, {"id": "http_context", "referrer": "https://rick.objectiv.io/", "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0", "remote_address": "144.144.144.144", "_type": "HttpContext"}, {"id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "cookie_id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "_type": "CookieIdContext"}]',
     '[{"_type": "WebDocumentContext", "id": "#document", "url": "https://rick.objectiv.io/"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "yep"}, {"_type": "SectionContext", "id": "cc91EfoBh8A"}]'],
    [2,
     '[{"_type": "ApplicationContext", "id": "rod-web-demo"}, {"id": "http_context", "referrer": "https://rick.objectiv.io/", "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0", "remote_address": "144.144.144.144", "_type": "HttpContext"}, {"id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "cookie_id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "_type": "CookieIdContext"}]',
     '[{"_type": "WebDocumentContext", "id": "#document", "url": "https://rick.objectiv.io/", "_types": ["AbstractContext", "AbstractLocationContext", "SectionContext", "WebDocumentContext"]}, {"_type": "NavigationContext", "id": "navigation", "_types": ["AbstractContext", "AbstractLocationContext", "NavigationContext", "SectionContext"]}]'],
    [3,
     '[{"_type": "ApplicationContext", "id": "rod-web-demo"}, {"id": "http_context", "referrer": "https://rick.objectiv.io/", "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0", "remote_address": "144.144.144.144", "_type": "HttpContext"}, {"id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "cookie_id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "_type": "CookieIdContext"}]',
     '[{"_type": "WebDocumentContext", "id": "#document", "url": "https://rick.objectiv.io/"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "new"}, {"_type": "SectionContext", "id": "BeyEGebJ1l4"}]'],
    [4,
     '[{"_type": "ApplicationContext", "id": "rod-web-demo"}, {"id": "http_context", "referrer": "https://rick.objectiv.io/", "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0", "remote_address": "144.144.144.144", "_type": "HttpContext"}, {"id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "cookie_id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "_type": "CookieIdContext"}]',
     '[{"_type": "WebDocumentContext", "id": "#document", "url": "https://rick.objectiv.io/"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "new"}, {"_type": "SectionContext", "id": "yBwD4iYcWC4"}]'],
    [5,
     '[{"_type": "ApplicationContext", "id": "rod-web-demo"}, {"id": "http_context", "referrer": "https://rick.objectiv.io/", "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0", "remote_address": "144.144.144.144", "_type": "HttpContext"}, {"id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "cookie_id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "_type": "CookieIdContext"}]',
     '[{"_type": "WebDocumentContext", "id": "#document", "url": "https://rick.objectiv.io/"}, {"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "new"}, {"_type": "MediaPlayerContext", "id": "eYuUAGXN0KM"}]'],
    [6,
     '[{"_type": "ApplicationContext", "id": "rod-web-demo"}, {"id": "http_context", "referrer": "https://rick.objectiv.io/", "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0", "remote_address": "144.144.144.144", "_type": "HttpContext"}, {"id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "cookie_id": "f84446c6-eb76-4458-8ef4-93ade596fd5b", "_type": "CookieIdContext"}]',
     '[{"_type": "WebDocumentContext", "id": "#document", "url": "https://rick.objectiv.io/"}]']

]
JSON_COLUMNS_REAL = ['event_id', 'global_contexts', 'location_stack']
