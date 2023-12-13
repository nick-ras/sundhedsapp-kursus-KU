from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import xmltodict
import httpx
from kivy.graphics import Color

#events_json = None

class MainApp(App):
        
    def __init__(self):
        App.__init__(self)
        
        self.username_label = Label(text="Username")
        self.password_label = Label(text="Password")
        self.graph_id_label = Label(text="Graph ID")
     
        #Login
        self.password = TextInput(hint_text="Enter username",  text="zBsn9iZWvDKb5YB")
        self.username = TextInput(hint_text="Enter username",  text="nickras10@gmail.com")
        self.graph_id = TextInput(hint_text="Enter graph id",  text="1702957")
    
        
        #lavet full layout lvl 0
        self.layout_0lvl_full = BoxLayout(orientation='horizontal')
        #lavet input og output lvl 1
        self.layout_1lvl_input = BoxLayout(orientation='vertical')
        self.layout_1lvl_output = BoxLayout(orientation='vertical')
        #lavet info section og button lvl 2
        self.lay_2lvl_user_info_section = BoxLayout(orientation='vertical')
        self.lay_2lvl_button = BoxLayout(orientation='vertical')
        #lavet boxlayout til username, password og graphid i lvl 3
        self.lay_3lvl_username= BoxLayout(orientation='horizontal')
        self.lay_3lvl_password = BoxLayout(orientation='horizontal')
        self.lay_3lvl_graphid = BoxLayout(orientation='horizontal')


    def build(self):
        #USER INPUT added 2 lvl til lvl 3
        self.lay_3lvl_username.add_widget(self.username_label)
        self.lay_3lvl_username.add_widget(self.username)
        self.lay_2lvl_user_info_section.add_widget(self.lay_3lvl_username)
        self.lay_3lvl_password.add_widget(self.password_label)
        self.lay_3lvl_password.add_widget(self.password)
        self.lay_2lvl_user_info_section.add_widget(self.lay_3lvl_password)
        self.lay_3lvl_graphid.add_widget(self.graph_id_label)
        self.lay_3lvl_graphid.add_widget(self.graph_id)
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
    
    def post_request(self):
        newsim_response = httpx.post(
            url=f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id.text}/sims",
            auth=(self.username.text, self.password.text))
        return newsim_response
    
    def get_request(self):
        get_req = httpx.get(
        "https://repository.dcrgraphs.net/api/graphs/" + self.graph_id.text +
        "/sims/" + self.simulation_id + "/events?filter=only-enabled",
        auth=(self.username.text, self.password.text))
        return get_req
    
    def text_to_json(self, response):
        events_xml = response.text
        events_xml_no_quotes = events_xml[1:len(events_xml)-1]
        events_xml_clean = events_xml_no_quotes.replace('\\\"', "\"")
        return xmltodict.parse(events_xml_clean)
    
    def create_instance(self):
        #logger ind og får et nyt simulation id
        newsim_response =  self.post_request()
        self.simulation_id = newsim_response.headers['simulationID']
        
        #viser events for den nye simulation
        next_activities_response = self.get_request()
        
        #formatting the xml to text
        events_json = self.text_to_json(next_activities_response)
        
        #skaber alle simulation buttons som classes
        self.create_buttons_of_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text), events_json)
        
        #skaber knapperne til de events der er enabled i dcr serveren
    def create_buttons_of_enabled_events(self, 
        graph_id: str,
        sim_id: str,
        auth: (str, str),
        events_json):
        
        #fjerner alle knapperne fra forrige simulation
        self.layout_1lvl_output.clear_widgets()
        
        # Hvis flere events så er det en liste af dicts tror jeg
        events = []
        if not isinstance(events_json['events']['event'], list):
            events = [events_json['events']['event']]
        else:
            events = events_json['events']['event']
        print(events)
        
        for e in events:
            s_inst = SimulationButton(
                    e['@id'],                
                    graph_id,                
                    sim_id,                
                    auth[0],                
                    auth[1],                     
                    e['@label']
                    )
            #Det farver pending gult, men virker ikke altid
            if e['@pending'] == 'true' or e['@EffectivelyPending'] == 'true':
                s_inst.color = (1,1,0,1)
            self.layout_1lvl_output.add_widget(s_inst)
            print("From loop in create..enabled_events    " + e['@id'])

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
        
        #http call to dcr server to execute event

    def post_with_event_id(self):
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/"
        f"{self.simulation_id}/events/{self.event_id}")
        httpx.post(url, auth=(self.username,self.password))

    def execute_event(self, instance):
        self.post_with_event_id()
        
        #Samme url som i create_instance
        next_activities_response = current_main_app_instance.get_request()
        
        events_json = current_main_app_instance.text_to_json(next_activities_response)
        
        #denne opdaterer current main app instance med ny events_json, og skaber nye knapper
        current_main_app_instance.create_buttons_of_enabled_events(self.graph_id, self.simulation_id, (self.username, self.password), events_json)

print("Starting app")

current_main_app_instance = None

if __name__ == '__main__':
    current_main_app_instance = MainApp()
    current_main_app_instance.run()
