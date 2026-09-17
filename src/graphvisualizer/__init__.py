from graphvisualizer.app import App 

def main() -> None:
    print("Hello from graphvisualizer!")

    a = App() 
    App.setAppMode("addVertex")
    a.run()
