#
# class Base():
#
#     def _2_doc(self, no_need_ks=[], need_none_v=False):
#         if no_need_ks is None:
#             no_need_ks = []
#         var_items = vars(self).items()
#         doc = {}
#         for p, v in var_items:
#             if (v is None and not need_none_v) or (p in no_need_ks):
#                 continue
#             doc[p] = v
#         return doc
#
#     def __str__(self):
#         return str(self._2_doc())
#
# ############### User ###################################
# class User(Base):
#
#     def __init__(self, user_id=None, user_name=None, pass_word=None, **kwargs):
#         self.user_id = user_id
#         self.user_name = user_name
#         self.pass_word = pass_word
#         self.source = kwargs.pop('source', 0) # source 0: local, 1: qq, 2: weibo
#         self.source_key = kwargs.pop('source_key', '0')
#         self.regist_time = kwargs.pop('source_key', )

