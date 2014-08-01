from libmproxy.flow import Response
from netlib.odict import ODictCaseless
import cgi
import re
from gzip import GzipFile
import StringIO
import time

XML_OK_RESPONSE = '''<?xml version="1.0" encoding="UTF-8"?>
                        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                            <plist version="1.0">
                                <dict>
                                    <key>iPhone6,2</key>
                                    <array>
                                        <string>powerDiagnostics</string>
                                    </array>
                                </dict>
                            </plist>'''


def request(context, flow):
    path = flow.request.path
    print 'Path is %s' % path
    if path == '/ios/TestConfiguration/1.2':
        respond(flow, XML_OK_RESPONSE)
    elif path == '/MR3Server/ValidateTicket?ticket_number=123456':
        respond(flow, XML_OK_RESPONSE)
    elif path == '/MR3Server/MR3Post':
        saveContent(flow, 'general')
        respond(flow, XML_OK_RESPONSE)
    elif path == '/ios/log/extendedUpload':
        saveContent(flow, 'power')
        respond(flow, XML_OK_RESPONSE)


def saveContent(flow, prefix):
    decodedData = StringIO.StringIO()
    decodedData.write(flow.request.get_decoded_content())

    contentType = flow.request.get_content_type()
    multipart_boundary_re = re.compile('^multipart/form-data; boundary=(.*)$')
    matches = multipart_boundary_re.match(contentType)

    decodedData.seek(0)

    query = cgi.parse_multipart( decodedData, {"boundary" : matches.group(1)})

    with open("%s-%s.tar.gz" % (prefix, time.strftime("%Y%m%d-%H%M%S")), "w") as logs:
        logs.write(query['log_archive'][0])

def respond(flow, content):
    resp = Response(flow.request,
                        [1,1],
                        200, "OK",
                        ODictCaseless([["Content-Type","text/xml"]]),
                        content,
                        None)
    flow.request.reply(resp)

