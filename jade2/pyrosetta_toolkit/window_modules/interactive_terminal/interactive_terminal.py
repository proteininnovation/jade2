"""
This is a modified version of source code from the Accerciser project
(http://live.gnome.org/accerciser).
 
Backend to the console plugin.
 
@author: Eitan Isaacson
@organization: IBM Corporation
@copyright: Copyright (c) 2007 IBM Corporation
@license: BSD
 
All rights reserved. This program and the accompanying materials are made 
available under the terms of the BSD which accompanies this distribution, and 
is available at U{http://www.opensource.org/licenses/bsd-license.php}
"""
 
import re
import sys
import os
from io import StringIO
import tkinter
import IPython
from functools import reduce

#Works by itself, but not able to import it into the GUI at this time.
class IterableIPShell:
  def __init__(self,argv=None,user_ns=None,user_global_ns=None,
               cin=None, cout=None,cerr=None, input_func=None):
    if input_func:
      IPython.iplib.raw_input_original = input_func
    if cin:
      IPython.Shell.Term.cin = cin
    if cout:
      IPython.Shell.Term.cout = cout
    if cerr:
      IPython.Shell.Term.cerr = cerr
 
    if argv is None:
      argv=[]
 
    # This is to get rid of the blockage that occurs during 
    # IPython.Shell.InteractiveShell.user_setup()
    IPython.iplib.raw_input = lambda x: None
 
    self.term = IPython.genutils.IOTerm(cin=cin, cout=cout, cerr=cerr)
    os.environ['TERM'] = 'dumb'
    excepthook = sys.excepthook
    self.IP = IPython.Shell.make_IPython(argv,user_ns=user_ns,
                                         user_global_ns=user_global_ns,
                                         embedded=True,
                                         shell_class=IPython.Shell.InteractiveShell)
    self.IP.system = lambda cmd: self.shell(self.IP.var_expand(cmd),
                                            header='IPython system call: ',
                                            verbose=self.IP.rc.system_verbose)
    sys.excepthook = excepthook
    self.iter_more = 0
    self.history_level = 0
    self.complete_sep =  re.compile('[\s\{\}\[\]\(\)]')
 
  def execute(self):
    self.history_level = 0
    orig_stdout = sys.stdout
    sys.stdout = IPython.Shell.Term.cout
    try:
      line = self.IP.raw_input(None, self.iter_more)
      if self.IP.autoindent:
        self.IP.readline_startup_hook(None)
    except KeyboardInterrupt:
      self.IP.write('\nKeyboardInterrupt\n')
      self.IP.resetbuffer()
      # keep cache in sync with the prompt counter:
      self.IP.outputcache.prompt_count -= 1
 
      if self.IP.autoindent:
        self.IP.indent_current_nsp = 0
      self.iter_more = 0
    except:
      self.IP.showtraceback()
    else:
      self.iter_more = self.IP.push(line)
      if (self.IP.SyntaxTB.last_syntax_error and
          self.IP.rc.autoedit_syntax):
        self.IP.edit_syntax_error()
    if self.iter_more:
      self.prompt = str(self.IP.outputcache.prompt2).strip()
      if self.IP.autoindent:
        self.IP.readline_startup_hook(self.IP.pre_readline)
    else:
      self.prompt = str(self.IP.outputcache.prompt1).strip()
    sys.stdout = orig_stdout
 
  def historyBack(self):
    self.history_level -= 1
    return self._getHistory()
 
  def historyForward(self):
    self.history_level += 1
    return self._getHistory()
 
  def _getHistory(self):
    try:
      rv = self.IP.user_ns['In'][self.history_level].strip('\n')
    except IndexError:
      self.history_level = 0
      rv = ''
    return rv
 
  def updateNamespace(self, ns_dict):
    self.IP.user_ns.update(ns_dict)
 
  def complete(self, line):
    split_line = self.complete_sep.split(line)
    possibilities = self.IP.complete(split_line[-1])
    if possibilities:
      common_prefix = reduce(self._commonPrefix, possibilities)
      completed = line[:-len(split_line[-1])]+common_prefix
    else:
      completed = line
    return completed, possibilities
 
  def _commonPrefix(self, str1, str2):
    for i in range(len(str1)):
      if not str2.startswith(str1[:i+1]):
        return str1[:i]
    return str1
 
  def shell(self, cmd,verbose=0,debug=0,header=''):
    stat = 0
    if verbose or debug: print(header+cmd)
    # flush stdout so we don't mangle python's buffering
    if not debug:
      input, output = os.popen4(cmd)
      print(output.read())
      output.close()
      input.close()
 
 
ansi_colors =  {'0;30': 'Black',
                '0;31': 'Red',
                '0;32': 'Green',
                '0;33': 'Brown',
                '0;34': 'Blue',
                '0;35': 'Purple',
                '0;36': 'Cyan',
                '0;37': 'LightGray',
                '1;30': 'DarkGray',
                '1;31': 'DarkRed',
                '1;32': 'SeaGreen',
                '1;33': 'Yellow',
                '1;34': 'LightBlue',
                '1;35': 'MediumPurple',
                '1;36': 'LightCyan',
                '1;37': 'White'}
 
 
class TkConsoleView(tkinter.Text):
  def __init__(self,root):
    tkinter.Text.__init__(self,root)
 
    # As the stdout,stderr etc. get fiddled about with we need to put any
    # debug output into a file
    self.debug=0
    if self.debug:
	    self.o = open('debug.out','w')
 
    # Keeps track of where the insert cursor should be on the entry line
    self.mark = 'scroll_mark'
    self.mark_set(self.mark,tkinter.END)
    self.mark_gravity(self.mark,tkinter.RIGHT)
 
    # Set the tags for colouring the text
    for code in ansi_colors:
      self.tag_config(code,
		      foreground=ansi_colors[code])
 
    self.tag_config('notouch') # Tag for indicating what areas of the widget aren't editable
 
 
    # colour_pat matches the colour tags and places these in a group
    # match character with hex value 01 (start of heading?) zero or more times, followed by
    # the hex character 1b (escape)  then "[" and group ...things.. followed by m (?) and then
    # hex character 02 (start of text) zero or more times
    self.color_pat = re.compile('\x01?\x1b\[(.*?)m\x02?')
 
    self.line_start = 'line_start' # Tracks start of user input on the line (excluding prompt)
    self.mark_set(self.line_start,tkinter.INSERT)
    self.mark_gravity(self.line_start,tkinter.LEFT)
 
    self._setBindings()
 
  def write(self, text, editable=False):
 
    segments = self.color_pat.split(text)
    # First is blank line
    segment = segments.pop(0)
 
    # Keep track of where we started entering text so we can set as non-editable
    self.start_mark = 'start_mark'
    self.mark_set(self.start_mark,tkinter.INSERT)
    self.mark_gravity(self.start_mark,tkinter.LEFT)
 
    self.insert(tkinter.END, segment)
 
    if segments:
      # Just return the colour tags
      ansi_tags = self.color_pat.findall(text)
 
      for tag in ansi_tags:
        i = segments.index(tag)
        self.insert(tkinter.END,segments[i+1],tag)
        segments.pop(i)
 
    if not editable:
      if self.debug:
          print("adding notouch between %s : %s" % ( self.index(self.start_mark),\
						     self.index(tkinter.INSERT) ))
 
      self.tag_add('notouch',self.start_mark,"%s-1c" % tkinter.INSERT)
 
    self.mark_unset(self.start_mark)    
    #jmht self.scroll_mark_onscreen(self.mark)
 
 
  def showBanner(self,banner):
    """Print the supplied banner on starting the shell"""
    self.write(banner)
 
  def showPrompt(self, prompt):
    self.write(prompt)
    self.mark_set(self.line_start,tkinter.INSERT)
    self.see(tkinter.INSERT) #Make sure we can always see the prompt
 
 
  def changeLine(self, text):
    self.delete(self.line_start,"%s lineend" % self.line_start) 
    self.write(text, True)
 
  def getCurrentLine(self):
 
    rv = self.get(self.line_start,tkinter.END)
 
    if self.debug:
        print("getCurrentline: %s" % rv, file=self.o)
	print("INSERT: %s" % tkinter.END, file=self.o)
	print("END: %s" % tkinter.INSERT, file=self.o)
	print("line_start: %s" % self.index(self.line_start), file=self.o)
 
    return rv
 
  def showReturned(self, text):
    self.tag_add('notouch',self.line_start,"%s lineend" % self.line_start )
    self.write('\n'+text)
    if text:
      self.write('\n')
    self.showPrompt(self.prompt)    
    #self.mark_set(self.line_start,Tkinter.END) #jmht don't need this as showprompt sets mark
 
  def _setBindings(self):
    """ Bind the keys we require.
        REM: if a bound function returns "break" then no other bindings are called
        If it returns None, then the other default bindings are called.
    """
    self.bind("<Key>",self.processKeyPress)
    self.bind("<Return>",self.processEnterPress)
    self.bind("<Up>",self.processUpPress)
    self.bind("<Down>",self.processDownPress)
    self.bind("<Tab>",self.processTabPress)
    self.bind("<BackSpace>",self.processBackSpacePress)
 
  def isEditable(self):
    """ Scan the notouch tag range in pairs and see if the INSERT index falls
        between any of them.
    """
    ranges = self.tag_ranges('notouch')    
    first=None
    for idx in ranges:
        if not first:
	    first=idx
	    continue
        else:
 
	    if self.debug:
	        print("Comparing %s between %s : %s " % (self.index(tkinter.INSERT),first,idx))
 
	    if self.compare( tkinter.INSERT,'>=',first ) and \
		   self.compare( tkinter.INSERT,'<=',idx ):
		return False
	    first=None
    return True
 
  def processKeyPress(self,event):
 
    if self.debug:
        print("processKeyPress got key: %s" % event.char, file=self.o)
        print("processKeyPress INSERT: %s" % self.index(tkinter.INSERT), file=self.o)
        print("processKeyPress END: %s" % self.index(tkinter.END), file=self.o)
 
    if not self.isEditable():
	    # Move cursor mark to start of line
	    self.mark_set(tkinter.INSERT,self.mark)
 
    # Make sure line_start follows inserted text
    self.mark_set(self.mark,"%s+1c" % tkinter.INSERT)
 
 
  def processBackSpacePress(self,event):
    if not self.isEditable():
	    return "break"
 
  def processEnterPress(self,event):
    self._processLine()
    return "break" # Need break to stop the other bindings being called
 
  def processUpPress(self,event):
    self.changeLine(self.historyBack())
    return "break"
 
  def processDownPress(self,event):
    self.changeLine(self.historyForward())
    return "break"
 
  def processTabPress(self,event):
    if not self.getCurrentLine().strip():
	    return
    completed, possibilities = self.complete(self.getCurrentLine())
    if len(possibilities) > 1:
	    slice = self.getCurrentLine()
	    self.write('\n')
	    for symbol in possibilities:
		    self.write(symbol+'\n')
	    self.showPrompt(self.prompt)
    self.changeLine(completed or slice)
    return "break"
 
class IPythonView(TkConsoleView, IterableIPShell):
  def __init__(self,root,banner=None):
    TkConsoleView.__init__(self,root)
    self.cout = StringIO()
    IterableIPShell.__init__(self, cout=self.cout,cerr=self.cout,
                             input_func=self.raw_input)
 
    if banner:
      self.showBanner(banner)
    self.execute()
    self.cout.truncate(0)
    self.showPrompt(self.prompt)
    self.interrupt = False
 
  def raw_input(self, prompt=''):
    if self.interrupt:
      self.interrupt = False
      raise KeyboardInterrupt
    return self.getCurrentLine()
 
  def _processLine(self):
    self.history_pos = 0
    self.execute()
    rv = self.cout.getvalue()
    if self.debug:
        print("_processLine got rv: %s" % rv, file=self.o)
    if rv: rv = rv.strip('\n')
    self.showReturned(rv)
    self.cout.truncate(0)
 
if __name__ == "__main__":
    root = tkinter.Tk()
    s=IPythonView(root)
    s.pack()    
    root.mainloop()
