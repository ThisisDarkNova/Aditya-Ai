from core.aditya_memory import memory_system

class AdityaKnowledge:
    @staticmethod
    def update_user_profile(key: str, value: str) -> str:
        """
        Updates the user profile persistently.
        Called by Aditya when she determines she needs to learn something new (e.g. key='mood', value='happy' or key='interest', value='piano').
        """
        try:
            print(f"[🧠 AdityaKnowledge] Memorizing: {key} = {value}")
            memory_system.update_profile(key, value)
            return f"Successfully saved {value} to {key}."
        except Exception as e:
            return f"Error saving memory: {e}"

# Global instance
learning_system = AdityaKnowledge()
