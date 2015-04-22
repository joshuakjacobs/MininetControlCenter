#!/usr/bin/python
from Tkinter import *
import subprocess
import time
import threading
import re


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


class Routeframe:

    def __init__(self,master):

        """Initialising variables and GUI elements.

        :param master:
        """
        self.i=1
        self.currentpacket=0
        self.oldpacket=0
        self.calc=0
        self.oldcalc=0
        self.s1=0
        self.p1=0
        self.d1=0
        self.s2=0
        self.p2=0
        self.d2=0
        self.run_flag = BooleanVar(root)
        self.run_flag.set(False)
        self.stop_threads = threading.Event()
        newframe = Frame(master, name='newframe')
        newframe.pack(fill=BOTH)

        #Window
        switchtext=Entry(newframe)
        porttext=Entry(newframe)
        desttext=Entry(newframe)
        actiontext=Entry(newframe)
        monitorswitch=Entry(newframe)
        monitorport=Entry(newframe)
        actiontext=Entry(newframe)

        self.label1=Label(newframe,text="Switch: ")
        self.label2=Label(newframe,text="In Port: ")
        self.label3=Label(newframe,text="Out Port: ")
        self.label4=Label(newframe,text="Packet Threshold: ")
        self.label5=Label(newframe,text="Route: ")
        self.label6=Label(newframe,text="Monitored Switch: ")
        self.label7=Label(newframe,text="Monitored Port: ")

        self.handler = lambda: self.save_routes(switchtext,porttext,desttext)

        self.routethread = RestartThread(target=lambda: self.route(monitorswitch,monitorport,actiontext))

        self.var = StringVar()
        self.var.set('Choose Priority')

        self.option = OptionMenu(newframe, self.var,'Primary','Secondary')
        self.option.grid(row=6,column=1)

        self.addbtn1 = Button(newframe, text="Save Route", command=self.handler)
        self.addbtn2= Button(newframe, text="Monitor", command=self.routethread.start)

        self.label1.grid(row=0,column=0)
        self.label2.grid(row=1,column=0)
        self.label3.grid(row=2,column=0)
        self.label4.grid(row=3,column=0)
        self.label5.grid(row=6,column=0)
        self.label6.grid(row=4,column=0)
        self.label7.grid(row=5,column=0)
        self.addbtn1.grid(row=7, column=0)
        self.addbtn2.grid(row=7, column=1)

        switchtext.grid(row=0,column=1)
        porttext.grid(row=1,column=1)
        desttext.grid(row=2,column=1)
        actiontext.grid(row=3,column=1)
        monitorswitch.grid(row=4,column=1)
        monitorport.grid(row=5,column=1)

    def save_routes(self,switchtext,porttext,desttext):

        """Function that saves Primary and Secondary routes
        :param switchtext:
        :param porttext:
        :param desttext:
        """
        priority=self.var.get()
        if priority=='Primary':
            self.s1=switchtext.get()
            self.p1=porttext.get()
            self.d1=desttext.get()
            string='sudo ovs-ofctl -O OpenFlow13 add-flow {} in_port={},priority=1,actions=output:{}'.format(self.s1,self.p1,self.d1)
            subprocess.Popen(string,shell=True)
            print "Saving Primary Rules",self.s1,self.p1,self.d1



        if priority=='Secondary':
            self.s2=switchtext.get()
            self.p2=porttext.get()
            self.d2=desttext.get()
            print "Saving Secondary Rules",self.s2,self.p2,self.d2

    def route(self,monitorswitch,monitorport,actiontext):

        """Main monitoring function. Reads external data file, implements 2nd route if packet threshold breached
        Currently set to read file every half second, can be set lower for higher accuracy.
        Reverts to Primary Rules after a set time - can also be modified here.

        :param monitorswitch:
        :param monitorport:
        :param actiontext:
        """
        global flag
        flag = True
        thresh=int(actiontext.get())
        s_monitor=monitorswitch.get()
        p_monitor=monitorport.get()

        self.run_flag.set(True)
        self.stop_threads.clear()
        self.addbtn2.configure(text='Stop Monitor', command=self.end_route)

        print "Monitoring.."

        regex='(dpid:'+s_monitor+' )(port:'+p_monitor+' )(packetcount:)(\d{1,100})'
        counter=0

        while not self.stop_threads.is_set():

            for line in reversed(open("data.txt").readlines()):

                match=re.search(regex,line)
                if match is not None:
                    self.currentpacket = int(match.group(4))
                    if flag is True:
                        self.oldpacket = self.currentpacket
                        flag=False
                    break

            self.calc=self.currentpacket - self.oldpacket
            print 'calc is: ',self.calc

            if (self.calc>thresh) and (self.oldcalc!=self.calc):

                self.i += 1
                string = 'sudo ovs-ofctl -O OpenFlow13 del-flows {} --strict in_port={},priority={}'.format(self.s2,self.p2,(self.i-1))
                string2= 'sudo ovs-ofctl -O OpenFlow13 add-flow {} in_port={},priority={},actions=output:{} '.format(self.s2,self.p2,self.i,self.d2)
                subprocess.Popen(string,shell=True)
                subprocess.Popen(string2,shell=True)
                self.oldpacket=self.currentpacket
                print "Installed Secondary Rules"
            else:
                time.sleep(0.5)
                counter += 1
                if counter == 75:
                    string='sudo ovs-ofctl -O OpenFlow13 del-flows {} --strict in_port={},priority={}'.format(self.s2,self.p2,self.i)
                    string2='sudo ovs-ofctl -O OpenFlow13 add-flow {} in_port={},priority=1,actions=output:{}'.format(self.s1,self.p1,self.d1)
                    subprocess.Popen(string,shell=True)
            subprocess.Popen(string2,shell=True)
            print self.i
                    print "Reverting to Primary Rules"
                    counter = 0

            self.oldcalc=self.calc

        def end_route(self):
            """Is called when the Stop Monitor button is clicked. Ends the monitoring thread independently, and
            reconfigures button to start the thread again

            """
            print "Stopping monitor"
            self.stop_threads.set()
            self.addbtn2.configure(text="Monitor", command=self.routethread.start)


def handler():
    root.quit()

if __name__ == "__main__":
    root = Tk()
    root.title('Routing')
    root.protocol("WM_DELETE_WINDOW", handler)  # To ensure application quits when closed
    app = Routeframe(root)

    root.mainloop()


