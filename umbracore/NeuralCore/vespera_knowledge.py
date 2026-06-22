from NeuralCore.vespera_memory import memory_system

class VesperaKnowledge:
    @staticmethod
    def update_user_profile(key: str, value: str) -> str:
        """
        Updates the user profile persistently.
        Called by Vespera when she determines she needs to learn something new (e.g. key='mood', value='happy' or key='interest', value='piano').
        """
        try:
            print(f"[🧠 VesperaKnowledge] Memorizing: {key} = {value}")
            memory_system.update_profile(key, value)
            return f"Successfully saved {value} to {key}."
        except Exception as e:
            return f"Error saving memory: {e}"

# Global instance
learning_system = VesperaKnowledge()
