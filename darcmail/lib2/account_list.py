#!/usr/bin/env python
######################################################################
## $Revision: 1.3 $
## $Date: 2016/02/11 23:38:41 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.platebtn as platebtn
import db_access as dba
import dm_common as dmc
import dm_wx
import paging
import account_info

####################################################################
## AccountList
####################################################################
class AccountList (wx.Panel):
  def __init__ (self, browse, results_notebook, name, cnx, data):
    wx.Panel.__init__ (self, parent=results_notebook, id=-1, name=name)
    self.browse = browse
    self.results_notebook = results_notebook
    self.results = results_notebook.GetParent()
    self.cnx  = cnx
    self.data = data
    row_count = len(self.data)
    self.pi = paging.PagingInfo(row_count)

    self.top_pane = wx.Panel(self, id=-1, name='top_pane')
    self.top_sizer  = wx.BoxSizer(orient=wx.HORIZONTAL)
    if row_count > dm_wx.MAX_LIST_SIZE:
      self.page_sizer = self.pi.page_links(self.pi.current_page, self.top_pane,
          self.OnPageButton)
      self.top_sizer.Add(self.page_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    self.top_pane.SetSizer(self.top_sizer)

    self.bot_pane = scrolled.ScrolledPanel(self, id=-1, name='bot_pane')
    self.gs = self.make_list(self.bot_pane)
    self.bot_pane.SetupScrolling()
    self.bot_pane.SetSizer(self.gs)

    self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.Add(self.top_pane, 0, wx.ALIGN_LEFT)
    self.sizer.Add(self.bot_pane, 1, wx.EXPAND|wx.ALIGN_LEFT)
    self.SetSizer(self.sizer)

    results_notebook.AddPage(self, str(self.results.page_id), select=True)
    self.browse.switch_to_results()

  ####################################################################
  def OnPageButton(self, event):
    eo = event.GetEventObject()
    label = eo.GetLabel()
    self.sizer.Hide(self.gs)
    self.gs.DeleteWindows()
    self.sizer.Hide(self.page_sizer)
    self.page_sizer.DeleteWindows()
    self.top_sizer.Remove(self.page_sizer)
    current_page = self.pi.current_page
    if label == '<<':
      self.page_sizer = self.pi.page_links_left(self.top_pane, self.OnPageButton)
    elif label == '>>':
      self.page_sizer = self.pi.page_links_right(self.top_pane, self.OnPageButton)
    else:
      current_page = int(label)
      self.page_sizer = self.pi.page_links(current_page, self.top_pane, self.OnPageButton)
    self.top_sizer.Add(self.page_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    self.top_pane.SetSizer(self.top_sizer)
    self.gs = self.make_list(self.bot_pane)
    self.bot_pane.SetSizer(self.gs)
    self.sizer.Layout()

  ####################################################################
  def make_list (self, parent):
    gs = wx.FlexGridSizer(cols=2)
    col1 = wx.StaticText(parent, id=-1, label='Id')
    col2 = wx.StaticText(parent, id=-1, label='Name')
    gs.Add(col1, 0, wx.ALIGN_CENTER)
    gs.Add(col2, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
    for i in range(self.pi.current_lo_i, self.pi.current_hi_i):
      (aid, name) = self.data[i]
      col1 = wx.lib.platebtn.PlateButton(parent, id=-1, name='aid_' + str(aid),
          label=str(aid), style=platebtn.PB_STYLE_SQUARE)
      col1.Bind(wx.EVT_BUTTON, self.OnAccountIdClick)
      col2 = wx.StaticText(parent, id=-1, name='', label=str(name))
      gs.Add(col1, 0, wx.ALIGN_LEFT)
      gs.Add(col2, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
    return gs

  ####################################################################
  def OnAccountIdClick(self, event):
    eo = event.GetEventObject()
    label = eo.GetLabel()
    aid   = int(label)
    busy = wx.BusyInfo('Collecting info for account ' + str(aid))
    account_info.AccountInfo('', self.browse, self.results_notebook,
        self.cnx, dba.DbAccount(self.cnx, aid))
    busy = None
    
