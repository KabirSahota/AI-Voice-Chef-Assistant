import os
import subprocess
import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
from groq import Groq

# ==========================================
# 1. SETUP YOUR FREE GROQ API KEY HERE
# ==========================================
GROQ_API_KEY = "YOUR_GROQ_KEY_HERE"
groq_client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. CORE UTILITY FUNCTIONS
# ==========================================
def clean_think_tags(text):
    """Wipes out any messy inner AI thinking blocks completely."""
    if "<think>" in text and "</think>" in text:
        text = text.split("</think>")[-1]
    return text.strip()

def mac_speak(text):
    """Forces your Mac's voice engine to read text aloud."""
    print(f"\n🎙️ AI Chef: {text}")
    subprocess.run(["say", "-v", "Daniel", text])

def auto_listen_voice(duration):
    """Automatically records your microphone for X seconds and translates it offline."""
    fs = 44100
    filepath = os.path.expanduser(f"~/Desktop/chef_voice_temp.wav")
    
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filepath, fs, myrecording)
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(filepath) as source:
            audio_data = recognizer.record(source)
            text_result = recognizer.recognize_google(audio_data)
            if os.path.exists(filepath):
                os.remove(filepath)
            return text_result.strip().lower()
    except Exception:
        if os.path.exists(filepath):
            os.remove(filepath)
        return ""

# ==========================================
# 3. AI RECIPE GENERATION
# ==========================================
def get_recipe(dish_name):
    print(f"\n👨‍🍳 Creating your custom master guide for {dish_name}...")
    prompt = (
        f"Provide an incredibly explicit, step-by-step cooking guide with exact pointers, "
        f"visual cues, and deep explanations for: {dish_name}. "
        f"Break the final recipe down into clearly numbered lines (Step 1, Step 2, etc.) "
        f"so it can be easily read out loud one step at a time. Do not include introductory notes."
    )
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a meticulous master chef. You give direct cooking instructions and filter out your inner thoughts."},
            {"role": "user", "content": prompt}
        ],
        model="qwen/qwen3.6-27b",
    )
    return clean_think_tags(chat_completion.choices.message.content)

# ==========================================
# 4. MAIN AUTOMATED WORKFLOW LOOP
# ==========================================
def main():
    mac_speak("Hello! What meal would you like to cook today?")
    dish = input("\nType your dish name here (e.g., Chocolate Cake) and press Enter: ")
    
    if not dish.strip():
        mac_speak("I didn't catch that. Please try running the program again.")
        return

    mac_speak(f"Perfect. Let me build the master recipe for {dish}. One moment.")
    
    try:
        raw_recipe = get_recipe(dish)
        lines = [line.strip() for line in raw_recipe.split('\n') if line.strip()]
        steps = [l for l in lines if not l.startswith('---')]
        
        mac_speak("Recipe is ready! After each step finishes playing, simply say next out loud.")
        
        current_step_index = 0
        while current_step_index < len(steps):
            step = steps[current_step_index]
            
            if not step or step.lower().startswith("here is") or step.lower().startswith("certainly"):
                current_step_index += 1
                continue
                
            # 1. Read step aloud
            mac_speak(step)
            
            # 2. Wait half a second, then open the mic automatically
            subprocess.run(["sleep", "0.5"])
            print("🔴 Listening for command ('next' or 'repeat')...")
            spoken_command = auto_listen_voice(4)
            print(f"🗣️ Heard word: '{spoken_command}'")
            
            # 3. Process structural movement decisions
            if "repeat" in spoken_command:
                mac_speak("Repeating that step.")
                continue
            else:
                # Defaults automatically forward to next card on "next" or silence
                current_step_index += 1
                
        mac_speak("That is the end of the recipe! Happy cooking!")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        mac_speak("Sorry, I ran into an error connecting to the AI network.")

if __name__ == "__main__":
    main()
