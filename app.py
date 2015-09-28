import cherrypy
import psycopg2
import keyring
import pangakupu as pk
import pū
import maoriword as mw
import pg_utils
import config


class Dummy():
    @cherrypy.expose
    def index(self):
          raise cherrypy.HTTPRedirect('/iwa')


class PangaKupu():

    def __init__(self, template_dir):
        from jinja2 import Environment, FileSystemLoader
        self.env = Environment(loader=FileSystemLoader(template_dir))
        cherrypy.config.update({'error_page.default': self.process_all_errors})


# ####################################################################
# PAGE - home
# ####################################################################
    @cherrypy.expose
    def index(self):
        db_access_info = pg_utils.get_db_access_info()
        with psycopg2.connect(database=db_access_info[0],
                              user=db_access_info[1],
                              password=db_access_info[2]) as connection:

            with connection.cursor() as cursor:

                one_9_letter_word_at_random_query = \
                    ' '.join((
                        "SELECT word FROM pgt_board_children",
                        "ORDER BY RANDOM() LIMIT 1",
                    ))

                cursor.execute(one_9_letter_word_at_random_query)
                word = cursor.fetchall()  # list of tuples [('word'),]

        connection.close()
        word = ''.join(word[0])
        koru = pk.get_koru(word)
        template_id = 'index'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id,
                                "word": word,
                                "koru": koru})


# ####################################################################
# PAGE - createboard
# ####################################################################
    @cherrypy.expose
    def createboard(self):

        MAX_CHILDREN = 265
        min_and_max_pairs = [(1, MAX_CHILDREN),
                             (1, 20),
                             (21, 50),
                             (51, 100),
                             (101, MAX_CHILDREN)]

        db_access_info = pg_utils.get_db_access_info()
        with psycopg2.connect(database=db_access_info[0],
                              user=db_access_info[1],
                              password=db_access_info[2]) as connection:

            with connection.cursor() as cursor:

                word_centre_letter_pairs = []
                for min, max in min_and_max_pairs:

                    one_random_row_board_children_query = \
                        ' '.join((
                            "SELECT * FROM pgt_board_children",
                            "WHERE number_of_children BETWEEN",
                            "{0} AND {1}".format(min, max),
                            "ORDER BY RANDOM() LIMIT 1",
                        ))

                    cursor.execute(one_random_row_board_children_query)
                    board_children_row = cursor.fetchall()  # list of 1 tuple
                    word = ''.join(board_children_row[0][0])
                    centre_letter = ''.join(board_children_row[0][1])
                    word_centre_letter_pairs.append((word, centre_letter))

        connection.close()

        # get the koru
        koru001 = pk.get_koru(word_centre_letter_pairs[0][0],
                              word_centre_letter_pairs[0][1])

        koru001020 = pk.get_koru(word_centre_letter_pairs[1][0],
                                 word_centre_letter_pairs[1][1])

        koru021050 = pk.get_koru(word_centre_letter_pairs[2][0],
                                 word_centre_letter_pairs[2][1])

        koru051100 = pk.get_koru(word_centre_letter_pairs[3][0],
                                 word_centre_letter_pairs[3][1])

        koru101 = pk.get_koru(word_centre_letter_pairs[4][0],
                              word_centre_letter_pairs[4][1])

        template_id = 'createboard'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id,
                                "koru001": koru001,
                                "koru001020": koru001020,
                                "koru021050": koru021050,
                                "koru051100": koru051100,
                                "koru101": koru101})


# ####################################################################
# PAGE - howtoplay
# ####################################################################
    @cherrypy.expose
    def howtoplay(self):
        template_id = 'howtoplay'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id})


# ####################################################################
# PAGE - about
# ####################################################################
    @cherrypy.expose
    def about(self):
        template_id = 'about'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id})


# ####################################################################
# PAGE - contact
# ####################################################################
    @cherrypy.expose
    def contact(self):
        template_id = 'contact'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id})


# ####################################################################
# PAGE - thankyou
# ####################################################################
    @cherrypy.expose
    def thankyou(self, feedback):

        '''
        Send an email to pangakupu@gmail.com
        Content is whatever they have entered.

        Need to connect to an smtp server
        Will probably be different from test to production
        '''
        cf = config.ConfigFile()
        test_or_production = (cf.configfile[cf.computername]['test_or_production'])

        # subject
        subject = (test_or_production.upper() +
                   ' ENVIRONMENT - Pangakupu Feedback')
        fromm = 'orotau@webfaction.com'  # not used by gmail
        to = 'pangakupu@gmail.com'
        contents = feedback

        self.send_mail(fromm, to, subject, contents)

        template_id = 'thankyou'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id})


# ####################################################################
# PAGE - board
# ####################################################################
    @cherrypy.expose
    def board(self, koru):

        children = pk.get_children(koru, koru[8])
        children_count = len(children)

        # allow template to hide border between digraphs
        digraph_starts = []
        # top row (these 2 are mutually exclusive)
        if koru[0] + koru[1] in pū.digraphs:
            digraph_starts.append(0)
        if koru[1] + koru[2] in pū.digraphs:
            digraph_starts.append(1)

        # bottom row (these 2 are mutually exclusive)
        if koru[6] + koru[5] in pū.digraphs:
            digraph_starts.append(6)
        if koru[5] + koru[4] in pū.digraphs:
            digraph_starts.append(5)

        template_id = 'board'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id,
                                "children_count": children_count,
                                "koru": koru,
                                "koru0": koru[0],
                                "koru1": koru[1],
                                "koru2": koru[2],
                                "koru3": koru[3],
                                "koru4": koru[4],
                                "koru5": koru[5],
                                "koru6": koru[6],
                                "koru7": koru[7],
                                "koru8": koru[8],
                                "digraph_starts": digraph_starts})


# ####################################################################
# PAGE - boardchildren
# ####################################################################
    @cherrypy.expose
    def boardchildren(self, koru):

        children = pk.get_children(koru, koru[8])
        children_count = len(children)

        # Sort
        children = sorted(children, key=mw.get_list_sort_key)

        # Group the children for display
        grouped_children = []
        if children_count <= 20:
            # one group
            grouped_children.append(children)
        elif children_count <= 60:
            # two groups
            if divmod(children_count, 2)[1] == 0:
                # even number
                group1_count = divmod(children_count, 2)[0]
                group2_count = group1_count
            elif divmod(children_count, 2)[1] == 1:
                # odd number
                group1_count = divmod(children_count, 2)[0] + 1
                group2_count = group1_count - 1
            grouped_children.append(children[:group1_count])
            grouped_children.append(children[-group2_count:])
        else:
            # three groups
            if divmod(children_count, 3)[1] == 0:
                # multiple of 3
                group1_count = divmod(children_count, 3)[0]
                group2_count = group1_count
                group3_count = group1_count
            elif divmod(children_count, 3)[1] == 1:
                # 1 left over (e.g. 61)
                group1_count = divmod(children_count, 3)[0] + 1
                group2_count = group1_count
                group3_count = group1_count - 2
            elif divmod(children_count, 3)[1] == 2:
                # 2 left over (e.g. 62)
                group1_count = divmod(children_count, 3)[0] + 1
                group2_count = group1_count
                group3_count = group1_count - 1
            grouped_children.append(children[:group1_count])
            grouped_children.append(children[group1_count:
                                             group1_count + group2_count])
            grouped_children.append(children[-group3_count:])

        # allow template to hide border between digraphs
        digraph_starts = []
        # top row (these 2 are mutually exclusive)
        if koru[0] + koru[1] in pū.digraphs:
            digraph_starts.append(0)
        if koru[1] + koru[2] in pū.digraphs:
            digraph_starts.append(1)

        # bottom row (these 2 are mutually exclusive)
        if koru[6] + koru[5] in pū.digraphs:
            digraph_starts.append(6)
        if koru[5] + koru[4] in pū.digraphs:
            digraph_starts.append(5)

        template_id = 'boardchildren'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id,
                                "grouped_children": grouped_children,
                                "children_count": children_count,
                                "koru": koru,
                                "koru0": koru[0],
                                "koru1": koru[1],
                                "koru2": koru[2],
                                "koru3": koru[3],
                                "koru4": koru[4],
                                "koru5": koru[5],
                                "koru6": koru[6],
                                "koru7": koru[7],
                                "koru8": koru[8],
                                "digraph_starts": digraph_starts})

    def send_mail(self, fromm, to, subject, contents):

        cf = config.ConfigFile()
        test_or_production = (cf.configfile[cf.computername]['test_or_production'])

        if test_or_production == 'test':
            # connect to smtp server for greenbay.graham@gmail.com
            import yagmail
            yag = yagmail.SMTP('greenbay.graham')
            yag.send(to=to, subject=subject, contents=yagmail.raw(contents))

        elif test_or_production == 'production':
            # connect to webfaction smtp server
            from smtplib import SMTP

            try:
                smtp = SMTP('smtp.webfaction.com', timeout=10)  # 10 seconds
            except:
                cherrypy.log("EMAIL FAIL 1 " + contents)
                raise
            else:
                with smtp:
                    try:
                        # get username and password for the webfaction mailbox
                        mail_access_info = self.get_mail_access_info()
                        smtp.login(mail_access_info[0], mail_access_info[1])
                    except:
                        cherrypy.log("EMAIL FAIL 2 " + contents)
                        raise
                    else:
                        try:
                            from email.mime.text import MIMEText
                            msg = MIMEText(contents)
                            msg['To'] = to
                            msg['From'] = fromm
                            msg['Subject'] = subject
                            smtp.send_message(msg)
                        except:
                            cherrypy.log("EMAIL FAIL 3 " + contents)
                            raise

    def process_all_errors(self, status, message, traceback, version):

        cf = config.ConfigFile()
        test_or_production = (cf.configfile[cf.computername]['test_or_production'])

        subject = (test_or_production.upper() +
                   ' ENVIRONMENT - Pangakupu - ' + status)
        fromm = "orotau@webfaction.com"
        to = "pangakupu@gmail.com"
        contents = status + message + traceback + version

        try:
            self.send_mail(fromm, to, subject, contents)
        except:
            #error sending email
            #don't raise another error
            cherrypy.log("EMAIL FAIL 4 " + fromm)
            cherrypy.log("EMAIL FAIL 4 " + to)
            cherrypy.log("EMAIL FAIL 4 " + subject)
            cherrypy.log("EMAIL FAIL 4 " + contents)
        finally:
            #make sure we show the correct error template, not the stack trace
            template_id = 'error'
            template = self.env.get_template(template_id + '.html')
            return template.render({"template_id": template_id})

    def get_mail_access_info(self):
        crac = cherrypy.request.app.config
        mailbox_user = crac['webfaction_mailbox']['user']
        mailbox_password = keyring.get_password(crac['webfaction_mailbox']
                                                    ['id'], mailbox_user)
        return mailbox_user, mailbox_password
