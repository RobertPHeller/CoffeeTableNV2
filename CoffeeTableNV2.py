#*****************************************************************************
#
#  System        : 
#  Module        : 
#  Object Name   : $RCSfile$
#  Revision      : $Revision$
#  Date          : $Date$
#  Author        : $Author$
#  Created By    : Robert Heller
#  Created       : Sun Oct 8 10:04:47 2023
#  Last Modified : <231008.1709>
#
#  Description	
#
#  Notes
#
#  History
#	
#*****************************************************************************
#
#    Copyright (C) 2023  Robert Heller D/B/A Deepwoods Software
#			51 Locke Hill Road
#			Wendell, MA 01379-9728
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# 
#
#*****************************************************************************


import Part, TechDraw, TechDrawGui
import FreeCADGui
from FreeCAD import Console
from FreeCAD import Base
import FreeCAD as App
import copy

from abc import ABCMeta, abstractmethod, abstractproperty

import os
import sys
sys.path.append(os.path.dirname(__file__))

import datetime

class Material(object):
    __instances__ = list()
    def __init__(self,name,*attributes):
        self.name=name
        self.__count__ = 1
        self.attrs=dict()
        for a in attributes:
            key,val = (a.split('='))
            self.attrs[key] = val
        Material.__instances__.append(self)
    def __match__(self,name,*attributes):
        if self.name != name:
            return False
        if len(attributes) != len(self.attrs):
            return False
        for a in attributes:
            key,val = (a.split('='))
            if key in self.attrs:
                if self.attrs[key] != val:
                    return False
            else:
                return False
        return True
    @classmethod
    def AddMaterial(cls,name,*attributes):
        for i in cls.__instances__:
            if i.__match__(name,*attributes):
                i.__count__ = i.__count__+1
                return i
        Material(name,*attributes)
    @classmethod
    def BOM(cls,filename):
        fp = open(filename,"w")
        cls.__instances__.sort(key=lambda m: m.name)
        for i in cls.__instances__:
            i.output(fp)
        fp.close()
    def output(self,fp):
        fp.write("%d,%s"%(self.__count__,self.name))
        for k in self.attrs:
            fp.write(",%s=%s"%(k,self.attrs[k]))
        fp.write("\n")
        
class GenerateDrawings(object):
    # doc.addObject('TechDraw::DrawSVGTemplate','USLetterLandscapeTemplate')
    # doc.USLetterTemplate.Template = App.getResourceDir()+"Mod/TechDraw/Templates/USLetter_Landscape.svg"
    # edt = doc.USLetterTemplate.EditableTexts    
    # "CompanyName"
    # "CompanyAddress"
    # "DrawingTitle1"
    # "DrawingTitle2"
    # "DrawingTitle3"
    # "DrawingNumber"
    # "Revision"
    # "DrawnBy"
    # "CheckedBy"
    # "Approved1"
    # "Approved2"
    # "Scale"
    # "Code"
    # "Weight"
    # "Sheet"
    # doc.USLetterTemplate.EditableTexts = edt
    # doc.addObject('TechDraw::DrawPage','name')
    # doc.name.Template = doc.USLetterTemplate
    # edt = doc.name.Template.EditableTexts
    # "DrawingTitle2"
    # "Scale"
    # "Sheet"
    # doc.name.Template.EditableTexts = edt
    __metaclass__ = ABCMeta
    @abstractmethod
    def generateDrawings(self,doc):
        pass
    def createTemplate(self,doc,title,numsheets,revision="A"):
        self.drawtemplate = doc.addObject('TechDraw::DrawSVGTemplate','USLetterLandscapeTemplate')
        self.drawtemplate.Template = App.getResourceDir()+"Mod/TechDraw/Templates/USLetter_Landscape.svg"
        edt = self.drawtemplate.EditableTexts
        edt['CompanyName'] = "Deepwoods Software"
        edt['CompanyAddress'] = '51 Locke Hill Road, Wendell, MA 01379 USA'
        edt['DrawingTitle1']= title
        edt['DrawingTitle3']= ""
        edt['DrawnBy'] = "Robert Heller"
        edt['CheckedBy'] = ""
        edt['Approved1'] = ""
        edt['Approved2'] = ""
        edt['Code'] = ""
        edt['Weight'] = ''
        edt['DrawingNumber'] = datetime.datetime.now().ctime()
        edt['Revision'] = revision
        self.drawtemplate.EditableTexts = edt
        self.sheet = 0
        self.sheetcount = numsheets
    def createSheet(self,doc,sheettitle,scale="1"):
        self.sheet = self.sheet + 1
        sheetname = "Sheet%dOf%d"%(self.sheet,self.sheetcount)
        thissheet = doc.addObject('TechDraw::DrawPage',sheetname)
        thissheet.Template = doc.copyObject(self.drawtemplate)
        edt = thissheet.Template.EditableTexts
        edt['DrawingTitle2']= sheettitle
        edt['Scale'] = scale
        edt['Sheet'] = "Sheet %d of %d"%(self.sheet,self.sheetcount)
        thissheet.Template.EditableTexts = edt
        thissheet.ViewObject.show()
        return thissheet
    
        


class CoffeeTableNV2(GenerateDrawings):
    __Length = 48*25.4
    __Width  = 30*25.4
    __BaseHeight = 8*25.4
    __ClearHeight = 7*25.4
    __TopBarHeight = 2*25.4
    __GlassThick = .25*25.4
    __FloorOffset = 1*25.4
    __LegSquare   = 2*25.4
    __CenterUnderHang = .5*25.4
    __BoardThick  = .75*25.4
    __NotchDepth  = .25*25.4
    __BirchPlyThick = .25*25.4
    __BirchColor = (210/255.0,180/255.0,140/255.0)
    __WoodColor = (139/255.0,35/255.0,35/255.0)
    __DrawerHeight = 3*25.4
    __DrawerLength = 16*25.4
    __DrawerOffBottom = 1*25.4
    __DrawerBottomNotch = .25*25.4
    __DrawerBottomNotchOffset = .5*25.4
    __BackDropColor = (1.0,1.0,1.0)
    __BackDropThick = .25*25.4
    # These three dims are from Everbilt D68816E-W-W Install Guide
    # CP3253028 ©2017 Liberty Hardware Manufacturing Corporation, A MASCO COMPANY REV 9/29/2017
    __DrawerSideClearance = 12.5
    __DrawerBottomClearance = 7
    __DrawerTopClearance = 16
    @classmethod
    def DrawerWidth(cls):
        centerSpace = cls.__Length - (2*((cls.__Length/3.0)+cls.__BoardThick))
        return centerSpace - (2*cls.__DrawerSideClearance)
    @classmethod
    def LegLength(cls):
        return (cls.__FloorOffset+cls.__BaseHeight+cls.__ClearHeight+\
                cls.__TopBarHeight)-cls.__GlassThick
    @classmethod
    def TableHeight(cls):
        return (cls.__FloorOffset+cls.__BaseHeight+cls.__ClearHeight+\
                cls.__TopBarHeight)
    def __init__(self,name,origin):
        self.name = name
        if not isinstance(origin,Base.Vector):
            raise RuntimeError("origin is not a Vector!")
        self.origin = origin
        self.__makeBase()
        self.__makeTopBar()
        self.__makeLegs()
        self.__makeGlassTop()
        self.__makeLexanSides()
    def __makeDrawer(self):
        dx = self.__Length/2.0 - (CoffeeTableNV2.DrawerWidth()/2.0)
        self.__drawerOrigin = self.__baseOrigin.add(Base.Vector(dx,0,\
                                            self.__DrawerOffBottom))
        drawerExtrude = Base.Vector(0,0,self.__DrawerHeight)
        no = self.__BoardThick-self.__NotchDepth
        lO = self.__drawerOrigin.add(Base.Vector(0,no,0))
        left = Part.makePlane(self.__BoardThick,self.__DrawerLength,\
                              lO)\
                .extrude(drawerExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__DrawerHeight/25.4),\
                             "length=%f"%(self.__DrawerLength/25.4))
        rX = CoffeeTableNV2.DrawerWidth()-self.__BoardThick
        rO = self.__drawerOrigin.add(Base.Vector(rX,no,0))
        right = Part.makePlane(self.__BoardThick,self.__DrawerLength,rO)\
                .extrude(drawerExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__DrawerHeight/25.4),\
                             "length=%f"%(self.__DrawerLength/25.4))
        bO = self.__drawerOrigin.add(Base.Vector(0,\
                                self.__DrawerLength,0))
        back = Part.makePlane(CoffeeTableNV2.DrawerWidth(),self.__BoardThick,\
                bO).extrude(drawerExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__DrawerHeight/25.4),\
                             "length=%f"%(CoffeeTableNV2.DrawerWidth()/25.4))
        fW = CoffeeTableNV2.DrawerWidth()+(2*self.__DrawerSideClearance)
        fO = self.__drawerOrigin.add(Base.Vector(-self.__DrawerSideClearance))
        front = Part.makePlane(fW,self.__BoardThick,fO).extrude(drawerExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__DrawerHeight/25.4),\
                             "length=%f"%(fW/25.4))
        front = front.cut(left)
        front = front.cut(right)
        botNO = self.__BoardThick-self.__DrawerBottomNotch
        botO = self.__drawerOrigin.add(Base.Vector(botNO,botNO,\
                                              self.__DrawerBottomNotchOffset))
        botW = CoffeeTableNV2.DrawerWidth()-botNO
        botL = self.__DrawerLength-botNO
        botThick = self.__BirchPlyThick
        bottom = Part.makePlane(botW,botL,botO)\
                                        .extrude(Base.Vector(0,0,botThick))
        Material.AddMaterial("birch plywood","thick=1/4",
                             "width=%f"%(botW/25.4),\
                             "length=%f"%(botL/25.4))
        front = front.cut(bottom)
        left = left.cut(bottom)
        right = right.cut(bottom)
        back = back.cut(bottom)
        self.drawerFront = front
        self.drawerLeft = left
        self.drawerRight = right
        self.drawerBack = back
        self.drawerBottom = bottom
    def __cutDrawerCutout(self):
        cW = self.__Length - (2*((self.__Length/3.0)+self.__BoardThick))
        cH = self.__DrawerHeight
        cO = self.__drawerOrigin.add(Base.Vector(-self.__DrawerSideClearance,\
                                                 0,0))
        cutout = Part.makePlane(cW,self.__BoardThick,cO)\
                   .extrude(Base.Vector(0,0,cH))
        self.baseFront = self.baseFront.cut(cutout)
    def __makeCenter(self):
        cX1 = self.__c1X
        cX2 = self.__c2X
        cLength = cX2 - cX1
        cYc = self.__Width / 2.0
        cY1 = cYc - (self.__LegSquare/2.0)
        centerOrigin = self.origin.add(Base.Vector(cX1,cY1,\
                                self.__FloorOffset-self.__CenterUnderHang))
        self.__centerOrigin = centerOrigin
        centerTop = CoffeeTableNV2.LegLength()
        cPostH = centerTop - (self.__FloorOffset-self.__CenterUnderHang)
        postExtrude = Base.Vector(0,0,cPostH)
        post1 = Part.makePlane(self.__BoardThick,self.__LegSquare,\
                               centerOrigin).extrude(postExtrude)
        post1 = post1.cut(self.baseCross1)
        post2 = Part.makePlane(self.__BoardThick,self.__LegSquare,\
                     centerOrigin.add(Base.Vector(cLength,0,0)))\
                     .extrude(postExtrude)
        post2 = post2.cut(self.baseCross2)
        top = Part.makePlane(cLength-self.__NotchDepth,self.__LegSquare,\
              centerOrigin.add(Base.Vector(self.__BoardThick-self.__NotchDepth,
                                           0,cPostH-self.__BoardThick)))\
                     .extrude(Base.Vector(0,0,self.__BoardThick))
        post1 = post1.cut(top)
        post2 = post2.cut(top)
        backZ = self.__CenterUnderHang+self.__BaseHeight+self.__BirchPlyThick
        back1O = centerOrigin.add(Base.Vector(0,-self.__BackDropThick,backZ))
        backL = cLength+self.__BoardThick
        backH = centerTop - back1O.z
        back1 = Part.makePlane(backL,self.__BackDropThick,back1O)\
                .extrude(Base.Vector(0,0,backH))
        back2O = centerOrigin.add(Base.Vector(0,self.__LegSquare,backZ))
        back2 = Part.makePlane(backL,self.__BackDropThick,back2O)\
                .extrude(Base.Vector(0,0,backH))
        self.centerPost1 = post1
        self.centerPost2 = post2
        self.centerTop = top
        self.centerBack1 = back1
        self.centerBack2 = back2
    def __makeBase(self):
        fo = self.__FloorOffset
        self.__baseOrigin = self.origin.add(Base.Vector(0,0,fo))
        baseExtrude = Base.Vector(0,0,self.__BaseHeight)
        front = Part.makePlane(self.__Length,self.__BoardThick,\
                               self.__baseOrigin)\
                .extrude(baseExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__BaseHeight/25.4),\
                             "length=%f"%(self.__Length/25.4))
        back = Part.makePlane(self.__Length,self.__BoardThick,\
                               self.__baseOrigin.add(Base.Vector(0,self.__Width-self.__BoardThick,0)))\
                .extrude(baseExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__BaseHeight/25.4),\
                             "length=%f"%(self.__Length/25.4))
        crossLength = self.__Width - (2*(self.__BoardThick-self.__NotchDepth))
        no = self.__BoardThick-self.__NotchDepth
        left = Part.makePlane(self.__BoardThick,crossLength,
                              self.__baseOrigin.add(Base.Vector(0,no,0)))\
                 .extrude(baseExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__BaseHeight/25.4),\
                             "length=%f"%(crossLength/25.4))
        right = Part.makePlane(self.__BoardThick,crossLength,
                              self.__baseOrigin.add(Base.Vector(self.__Length-self.__BoardThick,no,0)))\
                 .extrude(baseExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__BaseHeight/25.4),\
                             "length=%f"%(crossLength/25.4))
        front = front.cut(left)
        front = front.cut(right)
        back  = back.cut(left)
        back  = back.cut(right)
        c1o = self.__Length/3.0
        self.__c1X = c1o - (self.__BoardThick - self.__NotchDepth)
        c2o = self.__Length-((self.__Length/3.0)+self.__BoardThick)
        self.__c2X = c2o + self.__BoardThick - self.__NotchDepth
        cross1 = Part.makePlane(self.__BoardThick,crossLength,
                                self.__baseOrigin.add(Base.Vector(c1o,no,0)))\
                  .extrude(baseExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__BaseHeight/25.4),\
                             "length=%f"%(crossLength/25.4))
        cross2 = Part.makePlane(self.__BoardThick,crossLength,
                                self.__baseOrigin.add(Base.Vector(c2o,no,0)))\
                  .extrude(baseExtrude)
        Material.AddMaterial("Hardwood","thick=3/4",\
                             "width=%f"%(self.__BaseHeight/25.4),\
                             "length=%f"%(crossLength/25.4))
        front = front.cut(cross1)
        front = front.cut(cross2)
        back  = back.cut(cross1)
        back  = back.cut(cross2)
        self.baseFront = front
        self.baseBack  = back
        self.baseLeft = left
        self.baseRight = right
        self.baseCross1 = cross1
        self.baseCross2 = cross2
        self.__makeDrawer()
        self.__cutDrawerCutout()
        self.__makeCenter()
        
    def __makeTopBar(self):
        pass
    def __makeLegs(self):
        pass
    def __makeGlassTop(self):
        pass
    def __makeLexanSides(self):
        pass
    def show(self,doc=None):
        if doc==None:
            doc = App.activeDocument()
        obj = doc.addObject("Part::Feature",self.name+"_baseFront")
        obj.Shape = self.baseFront
        obj.Label = self.name+"_baseFront"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_baseBack")
        obj.Shape = self.baseBack
        obj.Label = self.name+"_baseBack"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_baseLeft")
        obj.Shape = self.baseLeft
        obj.Label = self.name+"_baseLeft"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_baseRight")
        obj.Shape = self.baseRight
        obj.Label = self.name+"_baseRight"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_baseCross1")
        obj.Shape = self.baseCross1
        obj.Label = self.name+"_baseCross1"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_baseCross2")
        obj.Shape = self.baseCross2
        obj.Label = self.name+"_baseCross2"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_drawerLeft")
        obj.Shape = self.drawerLeft
        obj.Label = self.name+"_drawerLeft"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_drawerRight")
        obj.Shape = self.drawerRight
        obj.Label = self.name+"_drawerRight"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_drawerBack")
        obj.Shape = self.drawerBack
        obj.Label = self.name+"_drawerBack"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_drawerFront")
        obj.Shape = self.drawerFront
        obj.Label = self.name+"_drawerFront"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_drawerBottom")
        obj.Shape = self.drawerBottom
        obj.Label = self.name+"_drawerBottom"
        obj.ViewObject.ShapeColor=self.__BirchColor
        obj = doc.addObject("Part::Feature",self.name+"_centerPost1")
        obj.Shape = self.centerPost1
        obj.Label = self.name+"_centerPost1"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_centerPost2")
        obj.Shape = self.centerPost2
        obj.Label = self.name+"_centerPost2"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_centerTop")
        obj.Shape = self.centerTop
        obj.Label = self.name+"_centerTop"
        obj.ViewObject.ShapeColor=self.__WoodColor
        obj = doc.addObject("Part::Feature",self.name+"_centerBack1")
        obj.Shape = self.centerBack1
        obj.Label = self.name+"_centerBack1"
        obj.ViewObject.ShapeColor=self.__BackDropColor
        obj = doc.addObject("Part::Feature",self.name+"_centerBack2")
        obj.Shape = self.centerBack2
        obj.Label = self.name+"_centerBack2"
        obj.ViewObject.ShapeColor=self.__BackDropColor



if __name__ == '__main__':
    doc = None
    for docname in App.listDocuments():
        if docname == 'CoffeeTableNV2':
            App.closeDocument(docname)
    doc = App.newDocument('CoffeeTableNV2')
    table = CoffeeTableNV2("CoffeeTable",Base.Vector(0,0,0))
    table.show(doc)
    App.ActiveDocument=doc
    Gui.ActiveDocument=doc
    Gui.SendMsgToActiveView("ViewFit")
    Gui.activeDocument().activeView().viewIsometric()
    Material.BOM("CoffeeTableNV2.bom")    
