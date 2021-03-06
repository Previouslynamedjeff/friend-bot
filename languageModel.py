import cohere


class Model:
    def __init__(self, api_key):
        self.co = cohere.Client(api_key)
        # Model generation variables
        self.model = 'medium'
        self.num_tokens = 50
        self.temperature = 1.2
        self.top_k = 0
        self.top_p = 0.75
        self.freq_penalty = 0.1
        self.pres_penalty = 0.1
        self.stop_seq = ["--"]
        self.return_likelihoods ='NONE'

        # stores a prompt for each user using the bot
        self.prompt = dict()
    
    # Converts a conversation to a cohere-styled prompt.
    def create_prompt(self, user_id: int, conversation: list): 
        # reset the prompt for the current user_id
        self.prompt[user_id] = f"Respond to a message\n{self.stop_seq[0]}\n" 

        for author, message in conversation:
            self.prompt[user_id] += f"{author}: {message}\n"
            
            if author == "bot":
                self.prompt[user_id] += f"{self.stop_seq[0]}\n"

        self.prompt[user_id] += f"bot:"
    
    def generate_response(self, user_id: int) -> tuple:
        response = ""
        appropriate = True
        
        try: 
            prediction = self.co.generate(
                model=self.model,
                prompt=self.prompt[user_id],
                max_tokens=self.num_tokens,
                temperature=self.temperature,
                k=self.top_k,
                p=self.top_p,
                frequency_penalty=self.freq_penalty,
                presence_penalty=self.pres_penalty,
                stop_sequences=self.stop_seq,
                return_likelihoods=self.return_likelihoods
            )
            response = prediction.generations[0].text

            # ignores extra output
            response = response.replace(self.stop_seq[0], '').strip().split('\n')[0]
        except cohere.CohereError as err:
            # blocked output
            print(err.message)
            if err.message.startswith("blocked output"):
                response = "That seems pretty rude..."
                appropriate = False
                print("Violation occured")
            else:
                response = "An error occured, please try again later."

        # space is here         vvvv   on purpose
        self.prompt[user_id] += f" {response}\n"
        
        return response, appropriate
