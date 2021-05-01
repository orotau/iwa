import cherrypy
import pangakupu as pk
import pū
import maoriword as mw
import difficulty_level
import sqlite3_utils
import config


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
        sqlite3_connection = sqlite3_utils.get_sqlite3_connection()
        cur = sqlite3_connection.cursor()

        word_centre_letter_at_random_query = \
            ' '.join((
                "SELECT * FROM board",
                "ORDER BY RANDOM() LIMIT 2",
            ))

        cur.execute(word_centre_letter_at_random_query)
        word_centre_letter = cur.fetchall()  # list of 1 tuple 

        sqlite3_connection.close()
        word_for_board = ''.join(word_centre_letter[0][0])
        centre_letter_for_board = ''.join(word_centre_letter[0][1])
        koru = pk.get_koru(word_for_board, centre_letter_for_board)
        word_for_display = ''.join(word_centre_letter[1][0])
        template_id = 'index'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id,
                                "word": word_for_display,
                                "koru": koru})


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
# PAGE - board
# ####################################################################
    @cherrypy.expose
    def board(self, koru):

        children = pk.get_children(koru, koru[8])
        groups = difficulty_level.group_children(children)        
        pai_count = len(groups[0])
        tino_pai_count = len(groups[0]) + len(groups[1])
        tino_pai_rawa_atu_count = len(groups[0]) + len(groups[1]) + len(groups[2])

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
                                "pai_count": pai_count,
                                "tino_pai_count": tino_pai_count,
                                "tino_pai_rawa_atu_count": tino_pai_rawa_atu_count,
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
        groups = difficulty_level.group_children(children)        
        pai_count = len(groups[0])
        tino_pai_count = len(groups[0]) + len(groups[1])
        tino_pai_rawa_atu_count = len(groups[0]) + len(groups[1]) + len(groups[2])

        #for use with existing code
        children_count = tino_pai_rawa_atu_count

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
                                "pai_count": pai_count,
                                "tino_pai_count": tino_pai_count,
                                "tino_pai_rawa_atu_count": tino_pai_rawa_atu_count,
                                "grouped_children": grouped_children,
                                "pai_words": [x[0] for x in groups[0]],
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
# PAGE - frequency (auau)
# ####################################################################
    @cherrypy.expose
    def auau(self, page = 1):
        return self.example(int(page), jumping)


    def process_all_errors(self, status, message, traceback, version):

        template_id = 'error'
        template = self.env.get_template(template_id + '.html')
        return template.render({"template_id": template_id})
        
