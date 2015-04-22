#!/usr/bin/python
__author__ = "Joshua K Jacobs, 2015"
__email__ = "joshuajac.2011@my.bristol.ac.uk"

from Tkinter import *
import subprocess
import threading
import json
import requests
import os
import signal
import ttk


class RestartThread(threading.Thread):  # A derived Thread class to enable threads to be restarted

    def __init__(self, target):
        super(RestartThread,self).__init__(target=target)
        self.target=target
        threading.Thread.__init__(self)

    def run(self):
        self.target()
        threading.Thread.__init__(self)

    def start(self):
        super(RestartThread,self).start()


class App:

    def __init__(self, master):

        """Initialisation of all GUI elements and variables

        :param master:
        """
        frame = Frame(master)
        frame.pack()

        textframe = Frame(master, relief=RAISED, borderwidth=1)
        textframe.pack(fill=BOTH, expand=True)

        self.controllerthread = RestartThread(target=self.controller_callback)
        self.mininetthread = RestartThread(target=self.mininet_callback)

        #Buttons
        self.minibutton = Button(frame,text="Run Network Topology",command=self.mininetthread.start)
        self.controlbutton = Button(frame,text="Run Controller",command=self.controllerthread.start)
        self.jsonbutton = Button(frame,text="Get Switches",command=self.dataprint)
        self.routebutton = Button(frame,text="Routing",command=self.routing_callback)
        self.quitbutton = Button(textframe,text="QUIT",fg="red",command=frame.quit)
        self.statsbutton = Button(frame, text="Display Stats", fg="red", command=self.getstats)
        self.addbutton = Button(frame, text="Add/Delete Flow", command=self.newframe)

        #arrangement
        self.minibutton.pack(side=LEFT,expand=True)
        self.controlbutton.pack(side=LEFT,expand=True)
        self.jsonbutton.pack(side=LEFT,expand=True)
        self.quitbutton.pack(side=BOTTOM,expand=True)
        self.addbutton.pack(side=RIGHT,expand=True)
        self.statsbutton.pack(side=RIGHT,expand=True)

        self.var = StringVar()
        self.var.set('Switches')
        self.option = OptionMenu(frame, self.var, ())
        self.option.config(width=7)
        self.option.pack(side=LEFT,expand=True)

        self.statvar = StringVar()
        self.statvar.set('Stats')
        self.statoption = OptionMenu(frame, self.statvar,'desc','flow','aggregateflow', 'port','queue')
        self.statoption.config(width=10)
        self.statoption.pack(side=LEFT,expand=True)
        self.routebutton.pack(side=RIGHT,expand=True)
        self.text =Text(textframe)
        self.text.pack(side=TOP,fill=BOTH,expand=True)
        self.text.tag_configure("stderr", foreground="#b22222")

        sys.stdout = TextRedirector(self.text, "stdout")
        sys.stderr = TextRedirector(self.text, "stderr")

    def newframe(self):

        """Creates a new child window for the manual add/delete flow functions.
        Uses tkinter Notebook library to create tabs

        """
        newroot = Toplevel()
        newframe = Frame(newroot, name='newframe')
        newframe.pack(fill=BOTH)

        #Notebook Tab creation within frame
        nb = ttk.Notebook(newframe, name='add/delete Flow')
        nb.grid()

        #First Tab
        add_flow = Frame(nb, name='add Flow')
        switchtext=Entry(add_flow)
        porttext=Entry(add_flow)
        actiontext=Entry(add_flow)
        label1=Label(add_flow,text="Switch: ")
        label2=Label(add_flow,text="In Port: ")
        label3=Label(add_flow,text="Out Port: ")
        handler = lambda: self.add_flow(newroot,switchtext,porttext,actiontext)
        addbtn = Button(add_flow, text="Add", command=handler)
        label1.grid(row=0,column=0)
        label2.grid(row=1,column=0)
        label3.grid(row=2,column=0)
        addbtn.grid(row=3, columnspan=2)
        switchtext.grid(row=0,column=1)
        porttext.grid(row=1,column=1)
        actiontext.grid(row=2,column=1)
        nb.add(add_flow, text="Add Flow") # add tab to Notebook

        #Second Tab
        delete_flow = Frame(nb, name='delete Flow')
        dswitchtext=Entry(delete_flow)
        dporttext=Entry(delete_flow)
        dlabel1=Label(delete_flow,text="Switch: ")
        dlabel2=Label(delete_flow,text="In Port: ")
        handler = lambda: self.del_flow(newroot,dswitchtext,dporttext)
        delbtn = Button(delete_flow, text="Delete", command=handler)
        dlabel1.grid(row=0,column=0)
        dlabel2.grid(row=1,column=0)
        delbtn.grid(row=3, columnspan=2)
        dswitchtext.grid(row=0,column=1)
        dporttext.grid(row=1,column=1)
        nb.add(delete_flow, text="Delete Flow")

        #Window Cancel Button
        btn = Button(newframe, text="Cancel", command=newroot.destroy)
        btn.grid(sticky=SE)

    def add_flow(self,newroot,switchtext,porttext,actiontext):

        """Function to add flow. Receives user input

        :param newroot:
        :param switchtext:
        :param porttext:
        :param actiontext:
        """
        s=switchtext.get()
        p=porttext.get()
        a=actiontext.get()
        string='sudo ovs-ofctl -O OpenFlow13 add-flow {} in_port={},priority=1,actions=output:{}'.format(s,p,a)
        subprocess.Popen(string,shell=True)
        newroot.destroy()

    def del_flow(self,newroot,dswitchtext,dporttext):

        """Function to delete flows. Receives user input

        :param newroot:
        :param dswitchtext:
        :param dporttext:
        """
        s=dswitchtext.get()
        p=dporttext.get()
        print s,p
        string='sudo ovs-ofctl -O OpenFlow13 del-flows {} in_port={}'.format(s,p)
        subprocess.Popen(string,shell=True)
        newroot.destroy()

    def controller_callback(self):
        """Callback function to start the controller.
        Reconfigures to stop the controller once called.

        """
        print "Starting Ryu.."
        task = subprocess.Popen('~/ryu/bin/ryu-manager --verbose --observe-links ~/ryu/ryu/app/gui_topology/gui_topology.py ~/ryu/ryu/app/ofctl_rest.py ~/MininetControlCenter/simple_monitor.py',
                                shell=True,preexec_fn=os.setsid)
        self.controlbutton.configure(text='Stop Controller', command=lambda: self.end_controller(task))

    def mininet_callback(self):
        """Callback function to run the custom topology script

        """
        print "Mininet will open in a new xterm window."
        subprocess.Popen('xterm -e sudo ~/MininetControlCenter/quickNet.py', shell=True)

    def routing_callback(self):
        """ Callback function to run the routing script

        """
        print "Prototype Routing willl open in a new window."
        subprocess.Popen('xterm -e sudo ~/routemonitor.py', shell=True)

    def dataprint(self):
        """
        Populates the dropdown menu option with list of switches.

        :return:
        """
        try:
            data=self.getdata()
            menu=self.option['menu']
            menu.delete(0,END)
            for d in data:
                menu.add_command(label='s%d'%d, command=lambda value=d: self.var.set(value))
                print d
            return data
        except:
            print "Failed to connect to controller - may not be running"
        return

    def end_controller(self,task):
        """Stops controller running.
        Param contains PID of the controller when started, used to kill the process automatically
        Reconfigures button to start controller again.

        :param task:
        """
        print "Stopping controller"
        os.killpg(task.pid,signal.SIGTERM)
        self.controlbutton.configure(text="Run Controller",command=self.controllerthread.start)

    def getdata(self):
        """
        Gets a list of switches in the network from server.
        Uses controller module and a JSON query to retrieve list.

        :return:
        """
        url = "http://127.0.0.1:8080/stats/switches"
        response = requests.get(url=url)
        code = response.status_code
        if int(code) == 200:
                data=json.loads(response.text)
                print data
                return data
        else:
                return

    def getstats(self):
        """Uses user input to retrieve his/her choice of statistics.
        Makes a JSON request to controller, who queries the switches.
        Data is prettyprinted JSON, sent to GUI

        :return:
        """
        dpid = self.var.get()
        stats = self.statvar.get()
        url = "http://127.0.0.1:8080/stats/{}/{}".format(stats,dpid)  # controller address
        response = requests.get(url=url)
        code = response.status_code
        if int(code) == 200:
                data=json.loads(response.text)
                print "\nREPLY FROM SWITCH %s:\n " % dpid
                print json.dumps(data, sort_keys=True, indent=1)
                return data
        else:
                return


class TextRedirector(object):  # Redirects text output from terminal to text box in GUI

    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(END)

if __name__ == "__main__":
    root = Tk()
    root.title('Mininet Control Center')
    app = App(root)

    root.mainloop()

