<template>
    <div class="chat-container">
      <div class="messages">
        <div v-for="(msg, index) in messages" :key="index" class="message">
          <strong>{{ msg.role }}:</strong> {{ msg.content }}
        </div>
      </div>
      <input v-model="input" @keyup.enter="sendMessage" placeholder="Type your message" />
      <button @click="sendMessage">Send</button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        input: "",
        messages: []
      };
    },
    methods: {
      async sendMessage() {
        if (!this.input) return;
        this.messages.push({ role: "You", content: this.input });
        const res = await fetch("http://127.0.0.1:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: this.input })
        });
        const data = await res.json();
        this.messages.push({ role: "Assistant", content: data.response });
        this.input = "";
      }
    }
  };
  </script>
  
  <style>
  .chat-container { max-width: 500px; margin: auto; }
  .messages { height: 300px; overflow-y: auto; margin-bottom: 10px; }
  .message { margin: 5px 0; }
  </style>
  