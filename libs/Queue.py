#-*- coding: utf-8 -*-


class Queue(object):
    def __init__(self, len):
        self.len = len
        self.queue = []

    def add(self, user):
        username = user["username"]
        if username in [q_user["username"] for q_user in self.queue]:
            for i, q_user in enumerate(self.queue):
                if q_user["username"] == username:
                    self.queue[i] = user
                    break
        else:
            if len(self.queue) < self.len:
                self.queue.append(user)
            else:
                self.queue = sorted(self.queue, key=lambda d: d["score"])
                if self.queue[-1]["score"] < user["score"]:
                    self.queue[-1] = user.copy()
