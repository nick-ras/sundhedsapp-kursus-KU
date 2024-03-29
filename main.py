from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import xmltodict
import httpx
import mysql.connector
from os import environ as env
from dotenv import load_dotenv

class MainApp(App):
    def __init__(self):
        App.__init__(self)
        
        self.username_label = Label(text="Username")
        self.password_label = Label(text="Password")
        self.graph_id_label = Label(text="Graph ID")
     
        #Login
        self.username = TextInput(hint_text="Enter username",text=env.get("DCR_LOGIN"))
        self.password = TextInput(hint_text="Enter password", password=True,text=env.get("DCR_PASS"))
        self.graph_id = TextInput(hint_text="Enter graph id",text="1704571")

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

        # Connect to the MySQL database
        try:
                self.cnx = mysql.connector.connect(
                    user=env.get("DB_USER"),
                    password=env.get("DB_PASS"),
                    host=env.get("DB_HOST"),
                    port=3306,
                    database=env.get("DATABASE"),
                    ssl_disabled=True
                )
                self.cursor = self.cnx.cursor()

                if self.cnx.is_connected():
                    print("Connection to MySQL database successful")

                    # Create a cursor object to interact with the database
                    cursor = self.cnx.cursor()

                    # SQL statement to create the DCRUsers table
    
                    self.cnx.commit()
                    temp = "USE `cloud-kursus`;"
                    cursor.execute(temp)

                    update_statement = """
                    UPDATE DCRUsers SET Role = 'Nurse' WHERE Email = %s;
                    """
                    data = (self.username.text,)
                    cursor.execute(update_statement, data)
                    self.cnx.commit()

                    select_statement = """
                    SELECT * FROM DCRTable;
                    """

                    cursor.execute(select_statement)
                    rows = cursor.fetchall()
                    print("DCRTable:")
                    for row in rows:
                        print(row)
                    select_statement2 = """
                    SELECT * FROM DCRUsers;
                    """
                    cursor.execute(select_statement2)
                    rows = cursor.fetchall()
                    print("DCRUsers:")
                    for row in rows:
                        print(row)
                
                    select_statement3 = f"""
                    SELECT Role FROM DCRUsers WHERE Email = %s;
                    """
                    data = (self.username.text,)
                    cursor.execute(select_statement3, data)
                    self.role = cursor.fetchone()

                    cursor.close()
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")

        

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
    
    def b_instance(self, instance):
        App.get_running_app().stop()

    def b_instance_terminate(self, instance):
        self.terminate_simulation()
        App.get_running_app().stop()
    
    def b_press(self, instance):
        self.create_instance()

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
        # Check if the graph_id already exists in DCRTable
        select_existing_statement = """
            SELECT * FROM DCRTable WHERE Graph_id = %s;
        """
        data = (self.graph_id.text,)
        self.cursor.execute(select_existing_statement, data)
        existing_row = self.cursor.fetchone()

        if existing_row:
            # If graph_id already exists, use the existing simulation_id
            self.simulation_id = str(existing_row[0])
        else:
            # If graph_id does not exist, create a new instance
            newsim_response = self.post_request()
            self.simulation_id = newsim_response.headers['simulationID']

        
        #viser events for den nye simulation
        next_activities_response = self.get_request()
        
        #formatting the xml to text
        events_json = self.text_to_json(next_activities_response)
        
        #skaber alle simulation buttons som classes
        self.create_buttons_of_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text), events_json)

        # Store the simulation for the new instance in the database
        self.store_simulation_in_database()



    def store_simulation_in_database(self):
        try:
            # Insert the simulation data into the database
            insert_statement = """
                INSERT INTO DCRTable (Simulation_id, Graph_id, Process_instance_name, Description)
                VALUES (%s, %s, %s, %s);
            """
            data = (self.simulation_id, self.graph_id.text, "PROCESS_INSTANCE_NAME", "DESCRIPTION")
            self.cursor.execute(insert_statement, data)
            self.cnx.commit()

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def terminate_simulation(self):
        try:
            # Check if there are no pending activities before terminating
            # Add your logic to check for pending activities

             #Delete the current simulation in the database
            delete_statement = """
                DELETE FROM DCRTable WHERE Graph_id = %s;
            """
            data = (self.graph_id.text,)
            self.cursor.execute(delete_statement, data)
            #delete_statement = """DELETE FROM DCRTable;"""
            #self.cursor.execute(delete_statement)
            self.cnx.commit()
            print(f"DCRTable cleared where graph_id = {self.graph_id.text}")

                    
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # Add the necessary modifications for terminate button and role-specific tasks
    def create_buttons_of_enabled_events(self, 
        graph_id: str,
        sim_id: str,
        auth: (str, str),
        events_json):
        
        #fjerner alle knapperne fra forrige simulation
        self.layout_1lvl_output.clear_widgets()
        
        # Hvis flere events så er det en liste af dicts events = []
        if not isinstance(events_json['events']['event'], list):
            events = [events_json['events']['event']]
        else:
            events = events_json['events']['event']
        
        self.lay_2lvl_button.clear_widgets()
        bu = Button(text="Terminate")
        self.lay_2lvl_button.add_widget(bu)
        counter = 0
        
        for e in events:
            if e['@roles'] == self.role[0]:
                s_inst = SimulationButton(
                        e['@id'],                
                        graph_id,                
                        sim_id,                
                        auth[0],                
                        auth[1],                     
                        e['@label']
                        )

                #Det farver pending gult
                if e['@pending'] == 'true' or e['@EffectivelyPending'] == 'true':
                    s_inst.color = (1,1,0,1)
                    counter += 1
                
                #if counter == 0:
                #    bu.bind(on_press=self.b_instance)   
                     
                self.layout_1lvl_output.add_widget(s_inst)
        if counter == 0:
            bu.bind(on_press=self.b_instance_terminate)  
        else:
            bu.bind(on_press=self.b_instance) 

class SimulationButton(Button):#, MainApp):
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
print("AAAAAAAAAAAAAAAAAAAA vAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
load_dotenv() 
temp = env.get('DB_USER')
print(temp)

current_main_app_instance = None
if __name__ == '__main__':
    current_main_app_instance = MainApp()
    current_main_app_instance.run()
