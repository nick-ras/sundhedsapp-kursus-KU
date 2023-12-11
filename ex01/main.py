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
        self.test1 = Label(text="test")
        self.test2 = Label(text="test")
        self.test3 = Label(text="test")
        self.username_label = Label(text="Username")
        self.password_label = Label(text="Password")
        self.graph_id_label = Label(text="Graph ID")
        
        #lavet lvl 0 og 1 boxlayouts
        self.layout_0lvl_full = BoxLayout(orientation='horizontal')
        self.layout_1lvl_input = BoxLayout(orientation='vertical')
        self.layout_1lvl_output = BoxLayout(orientation='vertical')
        

    def build(self):
        #lavet info section og button lvl 2
        lay_2lvl_user_info_section = BoxLayout(orientation='vertical')
        lay_2lvl_button = BoxLayout(orientation='vertical')
        
        #lavet boxlayout til username, passowrd og graphid i lvl 3
        lay_3lvl_username= BoxLayout(orientation='horizontal')
        lay_3lvl_password = BoxLayout(orientation='horizontal')
        lay_3lvl_graphid = BoxLayout(orientation='horizontal')
        
        #USER INPUT added 2 lvl til lvl 3
        lay_3lvl_username.add_widget(self.test1)
        lay_3lvl_username.add_widget(self.username_label)
        lay_2lvl_user_info_section.add_widget(lay_3lvl_username)
        lay_3lvl_password.add_widget(self.test2)
        lay_3lvl_password.add_widget(self.password_label)
        lay_2lvl_user_info_section.add_widget(lay_3lvl_password)
        lay_3lvl_graphid.add_widget(self.test3)
        lay_3lvl_graphid.add_widget(self.graph_id_label)
        lay_2lvl_user_info_section.add_widget(lay_3lvl_graphid)
        
        # #Button 3lvl added til lvl 2
        b = Button(text="Start Instance")
        b.bind(on_press=self.b_press)
        lay_2lvl_button.add_widget(b)
        
        # #Added lvl 2 til lvl 1
        self.layout_1lvl_input.add_widget(lay_2lvl_user_info_section)
        self.layout_1lvl_input.add_widget(lay_2lvl_button)
        #1 til 0 level
        self.layout_0lvl_full.add_widget(self.layout_1lvl_input)
        self.layout_0lvl_full.add_widget(self.layout_1lvl_output)
        
        return self.layout_0lvl_full
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
        self.layout_1lvl_output.clear_widgets()
        for e in events_json['events']['event']:
            self.layout_1lvl_output.add_widget(Label(text=e['@label']))
            print(e['@label'])
        
        #hvis den skalvises med det samme skal den ned i anden class ovenover
        
class SimulationButton(Button):
    def __init__(self, event_id: int,
            graph_id: str,
            simulation_id: str,
            username: str,
            password: str,
            text: str):
        Button.__init__(self)
        self.event_id = event_id
        self.text = text
        self.graph_id = graph_id
        self.simulation_id = simulation_id
        self.username = username
        self.password = password
        self.manipulate_box_layout: BoxLayout = BoxLayout()
        self.bind(on_press=self.execute_event)       

print("Starting app")

if __name__ == '__main__':
            MainApp().run()
