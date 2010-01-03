#!/usr/bin/env python

""" 
  PyPose: Bioloid pose system for arbotiX robocontroller
  Copyright (c) 2009, 2010 Michael E. Ferguson.  All right reserved.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software Foundation,
  Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import time, sys, serial
import wx

# Commander definitions
BUT_WALK1 = 1
BUT_WALK2 = 2
BUT_WALK3 = 4
BUT_LOOK4 = 8
BUT_LOOK5 = 16
BUT_LOOK6 = 32
BUT_WALKT = 64
BUT_LOOKT = 128

width = 300

class Commander(wx.Frame):
    TIMER_ID = 100

    def __init__(self, parent, ser):  
        wx.Frame.__init__(self, parent, -1, "ArbotiX Commander", style = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.ser = ser    

        sizer = wx.GridBagSizer(10,10)

        self.drive = wx.Panel(self,size=(width,width-20))
        self.drive.SetBackgroundColour('WHITE')
        self.drive.Bind(wx.EVT_MOTION, self.onMove)  
        wx.StaticLine(self.drive, -1, (width/2, 0), (1,width), style=wx.LI_VERTICAL)
        wx.StaticLine(self.drive, -1, (0, width/2), (width,1))
        sizer.Add(self.drive,(0,0),wx.GBSpan(2,1),wx.EXPAND|wx.ALL,5)
        self.forward = 0
        self.turn = 0

        # Selection for horizontal movement
        horiz = wx.StaticBox(self, -1, 'Horizontal Movement')
        horiz.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        horizBox = wx.StaticBoxSizer(horiz,orient=wx.VERTICAL) 

        self.selTurn = wx.RadioButton(self, -1, 'Turn', style=wx.RB_GROUP)
        horizBox.Add(self.selTurn)        
        self.selStrafe = wx.RadioButton(self, -1, 'Strafe')
        horizBox.Add(self.selStrafe)        
        sizer.Add(horizBox, (0,1), wx.GBSpan(1,1), wx.EXPAND|wx.TOP|wx.RIGHT,5)

        # Body rotations
        body = wx.StaticBox(self, -1, 'Body Movement')
        body.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        bodyBox = wx.StaticBoxSizer(body,orient=wx.VERTICAL) 
        bodySizer = wx.GridBagSizer(5,5)

        bodySizer.Add(wx.StaticText(self, -1, "Pan:"),(0,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        self.pan = wx.Slider(self, -1, 0, -100, 100, wx.DefaultPosition, (200, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        bodySizer.Add(self.pan,(0,1))
        bodySizer.Add(wx.StaticText(self, -1, "Tilt:"),(1,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        self.tilt = wx.Slider(self, -1, 0, -100, 100, wx.DefaultPosition, (200, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        bodySizer.Add(self.tilt,(1,1))
        bodySizer.Add(wx.StaticText(self, -1, "Roll:"),(2,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        self.roll = wx.Slider(self, -1, 0, -100, 100, wx.DefaultPosition, (200, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.roll.Disable()
        bodySizer.Add(self.roll,(2,1))
        bodyBox.Add(bodySizer) 
        
        sizer.Add(bodyBox, (1,1), wx.GBSpan(1,1), wx.EXPAND|wx.BOTTOM|wx.RIGHT,5)

        # timer for output
        self.timer = wx.Timer(self, self.TIMER_ID)
        self.timer.Start(33)
        wx.EVT_CLOSE(self, self.onClose)
        wx.EVT_TIMER(self, self.TIMER_ID, self.onTimer)

        self.SetSizerAndFit(sizer)
        self.Show(True)

    def onClose(self, event):
        self.timer.Stop()
        self.sendPacket(128,128,128,128,0)
        self.Destroy()

    def onMove(self, event=None):
        if event.LeftIsDown():        
            pt = event.GetPosition()
            self.forward = ((width/2)-pt[1])/2
            self.turn = (pt[0]-(width/2))/2           
        else:
            self.forward = 0
            self.turn = 0
            pass

    def onTimer(self, event=None):
        # configure output
        Xspeed = self.forward + 128
        Rspeed = self.turn + 128
        Pan = self.pan.GetValue()  + 128
        Tilt = self.tilt.GetValue()  + 128
        Buttons = 0
        if self.selStrafe.GetValue():
            Buttons = BUT_WALKT
        #print Xspeed, Rspeed, Pan, Tilt
        self.sendPacket(Xspeed, Rspeed, Tilt, Pan, Buttons)
        self.timer.Start(50)
        
    def sendPacket(self, Xspeed, Rspeed, Tilt, Pan, Buttons):
        # send output
        self.ser.write('\xFF')
        self.ser.write(chr(Xspeed))
        self.ser.write(chr(Rspeed))
        self.ser.write(chr(Tilt))
        self.ser.write(chr(Pan))
        self.ser.write(chr(Buttons))
        self.ser.write(chr(0))
        self.ser.write(chr(255 - ((Xspeed+Rspeed+Tilt+Pan+Buttons)%256)))
            
if __name__ == "__main__":
    # commander.py <serialport>
    ser = serial.Serial()
    ser.baudrate = 38400
    ser.port = sys.argv[1]
    ser.timeout = 0.5
    ser.open()
    
    app = wx.PySimpleApp()
    frame = Commander(None, ser)
    app.MainLoop()

