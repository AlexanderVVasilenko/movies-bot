class SetStateError(Exception):
    def __init__(self, user_id, value, current_state):
        self.user_id = user_id
        self.value = value
        self.current_state = current_state
        super().__init__(f"ERROR: Can't set {value} state from {current_state} for user {user_id}")
