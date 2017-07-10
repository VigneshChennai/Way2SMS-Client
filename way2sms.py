#!/usr/bin/python
import urllib
import urllib2
import cookielib
import sys
import time
import threading
from contextlib import contextmanager
from threading import Thread

from gi.repository import Gtk, GObject, Gdk

"""
This block sets the path to gtkbuild file

"""
argv = sys.argv[0]
splits = argv.split('/')
splits[-1] = "way2smsUI.xml"
UI_loc =""
if not len(splits) == 1:
    for i in splits:
        UI_loc = UI_loc + '/' + i
else:
    UI_loc = splits[0]

GObject.threads_init()
Gdk.threads_init()
    
class Way2smsService:
    service_name = "Way2sms"
    opener = None
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd
    def login(self):
        cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        data = urllib.urlencode({'username':self.user,
                                'password': self.passwd})
        ret = self.opener.open("http://site1.way2sms.com/Login1.action", data)
        return cookie,ret.geturl()
        
    def send_sms(self, number, msg):
        data = urllib.urlencode({'HiddenAction':'instantsms', 
                              'catnamedis':'Gudi Padwa',
                              'Action':'sdf5445fdg',
                              'MobNo':number,
                              'textArea':msg,
                            })
        ret = self.opener.open("http://site1.way2sms.com/quicksms.action", data)
        return ret.geturl()
        
    def send(self,number, msg):
        if self.opener != None:
            url = self.send_sms(number, msg)
            if 'logout.jsp' in url:
                cookie, ret_url = self.login()
	        if 'entry.action' in ret_url:
		    return {'status' : False, 'info': 'Invalid username or password'}
	        url = self.send_sms(number, msg)
	        if 'logout.jsp' in url:
	            return {'status' : False, 'info': 'Unable to send sms'}
        else:
            cookie, ret_url = self.login()
	    if 'entry.action' in ret_url:
	        return {'status' : False, 'info': 'Invalid username or password'}
	    url = self.send_sms(number, msg)
	    if 'logout.jsp' in url:
	        return {'status' : False, 'info': 'Unable to send sms'}
        return {'status': True, 'info': 'Successfully sent'}

        
class UI:
    sms_service = None
    @contextmanager
    def ui_lock(self):
        Gdk.threads_enter()
        yield
        Gdk.threads_leave()
        
    def on_window1_delete_event(self,widget,data=None):
        Gtk.main_quit()		
    def on_window1_destroy(self, widget, data=None):
        Gtk.main_quit()
    def send_sms(self):
        with self.ui_lock():
            self.button.set_label("Sending .........")
            self.button.set_sensitive(False)
        number = self.builder.get_object("entry1").get_text()
        textview = self.builder.get_object("textview1")
        with self.ui_lock():
            msg = textview.get_buffer().get_text(
                                        textview.get_buffer().get_start_iter()
                                        ,textview.get_buffer().get_end_iter(),False
                                        )
        ret = self.service.send(number, msg)
        if ret['status']:
            with self.ui_lock():
                self.button.set_label("Successfully Sent")
                self.textview.get_buffer().set_text("")
        else:    
            with self.ui_lock():
                self.button.set_label("Failed to Send")
        time.sleep(2)
        with self.ui_lock():
            self.button.set_label("Send")
            self.button.set_sensitive(True)

    def on_send_button_clicked(self,widget,data=None):
            Thread(target=self.send_sms).start()
    def on_keyrelease(self, widget, data=None):
        textview = self.builder.get_object("textview1")
        msg = textview.get_buffer().get_text(
                                    textview.get_buffer().get_start_iter()
                                    ,textview.get_buffer().get_end_iter(),False
                                    )
        if len(msg) >= 160:
            textview.get_buffer().set_text(msg[:160])
            return True
        else:
            return False
       
    def __init__(self, service):
        self.service = service
        if not hasattr(service, "service_name") or not hasattr(service, "send"):
            raise TypeError("Second argument (service) should be a " 
                             + "object of service (like Way2smsService)")
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_loc) 
        self.window = self.builder.get_object("main")
        self.window.set_title(service.service_name)
        self.builder.connect_signals(self)
        self.button = self.builder.get_object("button1")
        self.textview = self.builder.get_object("textview1")
        
def show(service, user, passwd):
    if not service == "way2sms":
        raise NotImplemented
    main = UI(service=Way2smsService(user, passwd))
    main.window.show()
    Gtk.main()
if __name__ == '__main__':
    show('way2sms', '9600187560', 'opensource' )
