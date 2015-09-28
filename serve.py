import os.path
import cherrypy

class Server():
    def __init__(self):

        # Get current directory
        # (from where the 'python serve.py' command is issued)
        base_dir = os.path.normpath(os.path.abspath(os.path.curdir))

        # Set configuration directory
        self.conf_dir = os.path.join(base_dir, "conf")

        # Update the global settings for the HTTP server and engine
        cherrypy.config.update(os.path.join(self.conf_dir, "server.cfg"))

        # Our application
        from app import PangaKupu

        # Specify the template directory that we use for jinja2 templates
        template_dir = os.path.join(base_dir, "templates")

        # Passing the template directory (there could be a better way)
        self.webapp = PangaKupu(template_dir)

    def run(self):
        '''
        See this URL for help
        http://docs.cherrypy.org/en/latest/basics.html#hosting-one-or-more-applications
        '''

        cherrypy.quickstart(self.webapp, '/iwa',
                            os.path.join(self.conf_dir, "app.cfg"))


if __name__ == '__main__':
    import config
    cf = config.ConfigFile()

    cherrypy.config.update({
        'server.socket_host': cf.configfile[cf.computername]['socket_host'],
        'server.socket_port': int(cf.configfile[cf.computername]['socket_port']),
        'engine.autoreload.on': cf.configfile[cf.computername]['autoreload']
    })

    Server().run()
