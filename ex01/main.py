from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import xmltodict
import httpx

#events_json = None

class MainApp(App):
        
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
        #lavet info section og button lvl 2
        self.lay_2lvl_user_info_section = BoxLayout(orientation='vertical')
        self.lay_2lvl_button = BoxLayout(orientation='vertical')
        #lavet boxlayout til username, passowrd og graphid i lvl 3
        self.lay_3lvl_username= BoxLayout(orientation='horizontal')
        self.lay_3lvl_password = BoxLayout(orientation='horizontal')
        self.lay_3lvl_graphid = BoxLayout(orientation='horizontal')


    def build(self):
        #USER INPUT added 2 lvl til lvl 3
        self.lay_3lvl_username.add_widget(self.test1)
        self.lay_3lvl_username.add_widget(self.username_label)
        self.lay_2lvl_user_info_section.add_widget(self.lay_3lvl_username)
        self.lay_3lvl_password.add_widget(self.test2)
        self.lay_3lvl_password.add_widget(self.password_label)
        self.lay_2lvl_user_info_section.add_widget(self.lay_3lvl_password)
        self.lay_3lvl_graphid.add_widget(self.test3)
        self.lay_3lvl_graphid.add_widget(self.graph_id_label)
        self.lay_2lvl_user_info_section.add_widget(self.lay_3lvl_graphid)
        
        # #Button 3lvl added til lvl 2
        b = Button(text="Start Instance")
        b.bind(on_press=self.b_press)
        self.lay_2lvl_button.add_widget(b)
        
        # #Added lvl 2 til lvl 1
        self.layout_1lvl_input.add_widget(self.lay_2lvl_user_info_section)
        self.layout_1lvl_input.add_widget(self.lay_2lvl_button)
        #1 til 0 level
        self.layout_0lvl_full.add_widget(self.layout_1lvl_input)
        self.layout_0lvl_full.add_widget(self.layout_1lvl_output)
        
        return self.layout_0lvl_full
    def b_press(self, instance):
        self.create_instance()
    #Viser workflow før man trykker på boxe
    def create_instance(self):
        #graph_id = "1702957" #self.graphid.text
        #logger ind og får et nyt simulation id
        newsim_response = httpx.post(
            url=f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
            auth=(self.username, self.password))
        #auth=(self.username.text, self.password.text))
        #print("VALDEMAR" + self.username, self.password)
        self.simulation_id = newsim_response.headers['simulationID']
        #print("New simulation created with id:", self.simulation_id)
        
        #viser events for den nye simulation
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
        
        #s = SimulationButton(self.graph_id,self.simulation_id, self.username, self.password, "hej")
        self.create_buttons_of_enabled_events(self.graph_id, self.simulation_id, (self.username, self.password), events_json)
        
        #skaber knapperne til de events der er enabled i dcr serveren
    def create_buttons_of_enabled_events(self, 
        graph_id: str,
        sim_id: str,
        auth: (str, str),
        events_json):
        
        #fjerner alle knapperne fra forrige simulation
        self.layout_1lvl_output.clear_widgets()
        
        # hvis 1 event vs flere events
        events = []
        if not isinstance(events_json['events']['event'], list):
            events = [events_json['events']['event']]
        else:
            events = events_json['events']['event']
        
            
        for e in events:
            s = SimulationButton(
                    e['@id'],                
                    graph_id,                
                    sim_id,                
                    auth[0],                
                    auth[1],                     
                    e['@label']
                    )

            s.manipulate_box_layout = self.layout_1lvl_output.add_widget
            #updaterer button_layout automatisk??
            self.layout_1lvl_output.add_widget(s)
            print("events_json = " + e['@id'])
            #her ?????????????????????????+
    def testfunc(self):
        self.test = "hey"
        print("inside testfunc")
        return("hey return")
      
class SimulationButton(Button, MainApp):
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
        print("event id in init  " + self.event_id)
        
        #http call to dcr server to execute event

    def execute_event(self, instance):
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/"
        f"{self.simulation_id}/events/{self.event_id}")

        #Request events
        httpx.post(url, auth=(self.username,self.password))
        
        #Change simulation ID according to where we are in list
        #self.simulation_id = newsim_response.headers['simulationID']
        #httpx.get(url)
        #httpx.post(url)
        #next_activities_response = httpx.get(url, auth=(self.username,self.password))
        #Samme url som i create_instance
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
        
        MainApp().create_buttons_of_enabled_events(self.graph_id, self.simulation_id, (self.username, self.password), events_json)
        
        #/api/graphs/{id}/sims/{simsid}/events
        # send a post request to dcr server with basic authentication
        # create the buttons of new enabled events <- explained in (5)

print("Starting app")

if __name__ == '__main__':
    mainApp = MainApp().run()
