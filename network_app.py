import pdb
pdb.set_trace()
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.slider import Slider


import numpy as np


class neuron_ball_widget(Widget):
	
	def __init__(self,**kwargs):
		
		super(neuron_ball_widget,self).__init__(**kwargs)
		
		
		with self.canvas:
			Color(1.,1.,1.,1)
			Ellipse(pos=self.pos,size=(40,40))
	
		


class Network(Widget):
	
	def __init__(self,**kwargs):
		
		
		
		super(Network,self).__init__(**kwargs)
		
		#self.test_ball = neuron_ball_widget(pos=(200,200),size=(40,40))
		#self.add_widget(self.test_ball)
		
		self.neuron_balls = []
		
		self.V = np.ndarray((0))
		self.V_t = np.ndarray((0))
		self.V_r = np.ndarray((0))
		self.E_l = np.ndarray((0))
		self.tau_m = np.ndarray((0))
		
		
		self.W = np.ndarray((0,0))
		self.running = False
		self.drawmode = "neuron"
		self.syn_create_list = []
		self.syn_list = []
		self.syn_drawing_instructions = []
		
	
	def on_touch_down(self,touch):
		
		r=20.
		
		if self.drawmode == "neuron":
			
			intersect = False
			
			
			for k in xrange(len(self.neuron_balls)):
								
				pos_x = self.neuron_balls[k].pos[0]+r
				pos_y = self.neuron_balls[k].pos[1]+r
				
				if ((pos_x-touch.x)**2+(pos_y-touch.y)**2)**0.5 <= 2*r:
					intersect = True
					
			if not(intersect):
				d=40.	
				#self.neuron_balls.append(Ellipse(pos=(touch.x-d/2.,touch.y-d/2.),size=(d,d)))
				self.neuron_balls.append(neuron_ball_widget(pos=(touch.x-d/2.,touch.y-d/2.),size=(d,d)))
				self.add_widget(self.neuron_balls[-1])
		
				self.V = np.append(self.V,-70.)
				self.V_t = np.append(self.V_t,-61.)
				self.V_r = np.append(self.V_r,-70)
				self.E_l = np.append(self.E_l,-60.)
				self.tau_m = np.append(self.tau_m,.6)
		
				W_old = np.array(self.W)
				self.W = np.zeros((self.W.shape[0]+1,self.W.shape[1]+1))
				#for k in xrange(self.W.shape[1]):
				#	self.W[:,k] = self.W[:,k]*2.*((np.random.rand()>0.5) - 0.5)
				#	self.W[k,k] = 0.
				self.W[:-1,:-1] = W_old
				#self.W[:-1,-1] = (np.random.rand(self.W.shape[0]-1))*2.
				#self.W[-1,:-1] = (np.random.rand(self.W.shape[1]-1))*2.
		
		if self.drawmode == "synapse":
			for k in xrange(len(self.neuron_balls)):
				
				pos_x = self.neuron_balls[k].pos[0]+r
				pos_y = self.neuron_balls[k].pos[1]+r
				
				if ((pos_x-touch.x)**2+(pos_y-touch.y)**2)**0.5 <= r:
				
				
				#if self.neuron_balls[k].collide_point(touch.x,touch.y):
					self.syn_create_list.append(k)
					if len(self.syn_create_list) == 2:
							
						weight = self.parent.toolbar.weight_slider.value
						wmax = self.parent.toolbar.weight_slider.max
						wmin = self.parent.toolbar.weight_slider.min
							
						
							
						if not(self.syn_create_list in self.syn_list) and self.syn_create_list[0] != self.syn_create_list[1]:
							
							offset = 10.	
								
							linepoints=[self.neuron_balls[self.syn_create_list[0]].pos[0]+20,
							 		self.neuron_balls[self.syn_create_list[0]].pos[1]+20,
							 		self.neuron_balls[self.syn_create_list[1]].pos[0]+20,
							 		self.neuron_balls[self.syn_create_list[1]].pos[1]+20]
						 	length = ((linepoints[0]-linepoints[2])**2+(linepoints[1]-linepoints[3])**2)**0.5
						 	shift = [offset*(linepoints[3]-linepoints[1])/length,-offset*(linepoints[2]-linepoints[0])/length]
						 	linepoints=[linepoints[0]+shift[0],
							 		linepoints[1]+shift[1],
							 		linepoints[2]+shift[0],
							 		linepoints[3]+shift[1]]
							cr = max(0,weight/wmax)
							cb = max(0,weight/wmin)
							cg = min(-weight/wmin+1.,-weight/wmax+1.)
							c = Color(cr,cg,cb)
							self.syn_drawing_instructions.append([c,Line(points=linepoints,width=2)])
							
							self.canvas.before.add(self.syn_drawing_instructions[-1][0])
							self.canvas.before.add(self.syn_drawing_instructions[-1][1])
							 	
							self.syn_list.append(self.syn_create_list)
							self.W[self.syn_create_list[1],self.syn_create_list[0]] = weight
						
						elif self.syn_create_list in self.syn_list:
							
							self.canvas.before.remove(self.syn_drawing_instructions[self.syn_list.index(self.syn_create_list)][0])
							self.canvas.before.remove(self.syn_drawing_instructions[self.syn_list.index(self.syn_create_list)][1])
							#pdb.set_trace()
							del self.syn_drawing_instructions[self.syn_list.index(self.syn_create_list)]
							self.syn_list.remove(self.syn_create_list)
							self.W[self.syn_create_list[1],self.syn_create_list[0]] = 0.
							 	
						self.syn_create_list = []
							
						
			
			
		
			
	def startstopsim(self):
		if not(self.running):
			self.scheduled_update = Clock.schedule_interval(self.update,1./60.)
			self.running = True
		else:
			Clock.unschedule(self.scheduled_update)
			self.running = False
	
	def update(self,dt):
		
		self.V += dt*(-(self.V-self.E_l)/self.tau_m)
		spikes = (self.V >= self.V_t)*1.
		self.V = self.V*(self.V < self.V_t) + self.V_r*(self.V >= self.V_t)
		
		
		
		self.V += np.dot(self.W,spikes)
		
		
		for k in xrange(len(self.neuron_balls)):
			self.neuron_balls[k].canvas.clear()
			with self.neuron_balls[k].canvas:
				
				c = round(0.15+0.85*(self.V[k]-self.V_r[k])/(self.V_t[k]-self.V_r[k]),6)
				Color(c,c,c,1)
				Ellipse(pos=self.neuron_balls[k].pos,size=self.neuron_balls[k].size)
			#self.neuron_balls[k].opacity = round(0.05+0.95*(self.V[k]-self.V_r[k])/(self.V_t[k]-self.V_r[k]),6)
		
		#with self.canvas:
		#	self.canvas.clear()
		#	for k in xrange(len(self.neuron_balls)):
				
				
				
		#		Color(0.,1.,1.,0.1+0.8*(self.V[k]-self.V_r[k])/(self.V_t[k]-self.V_r[k]))
		#	
		#		self.neuron_balls[k] = Ellipse(pos=self.neuron_balls[k].pos,size=self.neuron_balls[k].size)




class App_Widget(BoxLayout):

	def startstop(self,instance):
		self.network.startstopsim()
		if self.toolbar.startstop_button.text == "start":
			self.toolbar.startstop_button.text = "stop"
		else:
			self.toolbar.startstop_button.text = "start"
	
	def set_drawmode_neuron(self,instance):
		self.network.drawmode = "neuron"
	
	def set_drawmode_synapse(self,instance):
		self.network.drawmode = "synapse"	
	
	def __init__(self,**kwargs):
		
		super(App_Widget,self).__init__(**kwargs)
		
		
		
		#self.startstop_button = Button(text = "start",size_hint=(.2,.1))
		#self.startstop_button.bind(on_press=self.startstop)
		
		#self.add_neuron_button = Button(text = "add_neuron", size_hint=(.2,.1))
		
		self.toolbar = toolbar(size_hint=(1,.1),orientation='horizontal')
		
		self.network = Network(size_hint=(1,.9))
		
		#self.add_widget(self.startstop_button)
		#self.add_widget(self.add_neuron_button)
		self.add_widget(self.network,index=1)
		self.add_widget(self.toolbar,index=0)
		
		
		self.toolbar.startstop_button.bind(on_press=self.startstop)
		self.toolbar.add_neuron_button.bind(on_press=self.set_drawmode_neuron)
		self.toolbar.add_synapse_button.bind(on_press=self.set_drawmode_synapse)
		
		
class toolbar(BoxLayout):
	
	
	
	def __init__(self,**kwargs):
		
		super(toolbar,self).__init__(**kwargs)
		
		self.startstop_button = Button(text = "start",size_hint=(.2,1))
		#self.startstop_button.bind(on_press=self.get_parent_window().startstop)
		
		self.add_neuron_button = Button(text = "add/rem. neuron", size_hint=(.2,1))
		
		self.add_synapse_button = Button(text = "add/rem. connection", size_hint=(.2,1))
		
		self.weight_slider = Slider(min=-5.,max=5.,value=0.,value_track=True, value_track_color=[1, 0, 0, 1],size_hint=(.4,1))
		
		self.add_widget(self.startstop_button)
		self.add_widget(self.add_neuron_button)
		self.add_widget(self.weight_slider)
		self.add_widget(self.add_synapse_button)
		



class Network_App(App):
	
	def build(self):
		
		return App_Widget(orientation='vertical')

if __name__ == "__main__":
	
	Network_App().run()
