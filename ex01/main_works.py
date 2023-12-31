from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import xmltodict
import httpx

class MainApp(App):
    def __init__(self):
        App.__init__(self)
        
    def __init__(self):
        App.__init__(self)
        self.password = "zBsn9iZWvDKb5YB" #TextInput(hint_text="Enter password", password=True)
        self.username = "nickras10@gmail.com" #TextInput(hint_text="Enter username")
        self.graph_id = "1702957"# self.graphid = TextInput(hint_text="Enter graphid")
        self.username_label = Label(text="Username")
        self.password_label = Label(text="Password")
        self.graph_id_label = Label(text="Graph ID")
        
        self.layout_box1 = BoxLayout(orientation='vertical')
        

    def build(self):
        b_inner = BoxLayout(orientation='vertical')
        b_inner.add_widget(self.username_label)
        b_inner.add_widget(self.password_label)
        b_inner.add_widget(self.graph_id_label)
        #b_inner.add_widget(self.username)
        #b_inner.add_widget(self.password)
        #b_inner.add_widget(self.graphid)
        
        b = Button(text="Start Instance")
        b.bind(on_press=self.b_press)
        self.b_outer = BoxLayout()
        self.b_outer.add_widget(b_inner)
        self.b_outer.add_widget(b)
        self.b_outer.add_widget(self.layout_box1)
        
        return self.b_outer

    def b_press(self, instance):
        self.create_instance()

    def create_instance(self):
        #graph_id = "1702957" #self.graphid.text
        newsim_response = httpx.post(
            url=f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
            auth=(self.username, self.password))#auth=(self.username.text, self.password.text))
        print("VALDEMAR" + self.username, self.password)
        
        self.simulation_id = newsim_response.headers['simulationID']
        print("New simulation created with id:", self.simulation_id)
        
        

        next_activities_response = httpx.get(
        "https://repository.dcrgraphs.net/api/graphs/" + self.graph_id +
        "/sims/" + self.simulation_id + "/events?filter=only-enabled",
        auth=(self.username, self.password))
        
        #auth=(self.username.text, self.password.text))
        
        #formatting the xml to text
        events_xml = next_activities_response.text
        events_xml_no_quotes = events_xml[1:len(events_xml)-1]
        events_xml_clean = events_xml_no_quotes.replace('\\\"', "\"")
        
        #translate to json dict
        events_json = xmltodict.parse(events_xml_clean)
        
        #terate through all the events and add each label from the event as a Label in our UI. 
        # Access all events by going to the ['events']['event'] entry
        for e in events_json['events']['event']:
            self.layout_box1.add_widget(Label(text=e['@label']))
            print(e['@label'])
            

print("Starting app")

if __name__ == '__main__':
            MainApp().run()
