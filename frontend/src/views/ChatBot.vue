<template>
    <div class="chat-wrapper">
        <h1>向AI医生咨询</h1>
        <div class="chat-container" ref="chatContainer">
            <p class="thinking" v-if="isThinking">正在输入...</p>
            <div v-for="(msg, index) in messages" :key="index"
                :class="['chat-message', msg.role === 'user' ? 'user-message' : 'ai-message']">
                {{ msg.content }}
            </div>
        </div>

        <input v-model="question" @keydown.enter.prevent="sendQuestion" type="text" placeholder="请输入您的问题..." required />
        <button @click="sendQuestion">提交问题</button>
    </div>
</template>

<script>
export default {
    name: 'ChatBot',
    data() {
        return {
            question: '',
            messages: [],
            chatHistory: [],
            isThinking: false
        }
    },
    methods: {
        async sendQuestion() {
            const trimmed = this.question.trim()
            if (!trimmed) {
                alert('请输入您的问题！')
                return
            }

            // 添加用户消息
            this.messages.push({ role: 'user', content: trimmed })
            this.chatHistory.push({ role: 'user', content: trimmed })
            this.question = ''
            this.isThinking = true

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: trimmed, history: this.chatHistory })
                })

                if (!response.ok) throw new Error('HTTP 错误：' + response.status)

                await this.streamMessage(response)

            } catch (error) {
                this.isThinking = false
                this.messages.push({ role: 'assistant', content: '请求错误：' + error.message })
            }
        },
        async streamMessage(response) {
            const reader = response.body.getReader()
            const decoder = new TextDecoder('utf-8')

            let aiMsg = ''
            const newMsg = { role: 'assistant', content: '' }
            this.messages.push(newMsg)
            this.$nextTick(this.scrollToBottom)

            while (true) {
                const { value, done } = await reader.read()
                if (done) break

                const text = decoder.decode(value, { stream: true })
                newMsg.content += text
                aiMsg += text
                this.$nextTick(this.scrollToBottom)
            }

            this.chatHistory.push({ role: 'assistant', content: aiMsg })
            this.isThinking = false
        },
        scrollToBottom() {
            const container = this.$refs.chatContainer
            container.scrollTop = container.scrollHeight
        }
    },
    mounted() {
        this.question = '你是一个AI医生，请你帮助我回答任何医疗问题'
        this.sendQuestion()
    }
}
</script>

<style scoped>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    padding: 20px;
    background-color: #f7f7f7;
    max-width: 800px;
    margin: 0 auto;
}

h1 {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 20px;
}

.chat-container {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
    position: relative;
    /* 保证容器内的元素能定位 */
}

.chat-message {
    padding: 10px;
    border-radius: 5px;
    max-width: 80%;
    word-wrap: break-word;
}

.user-message {
    background-color: #e0f7fa;
    align-self: flex-end;
}

.ai-message {
    background-color: #f1f1f1;
    align-self: flex-start;
}

input,
button {
    padding: 10px;
    font-size: 16px;
    margin-top: 10px;
    width: 100%;
    border-radius: 5px;
    border: 1px solid #ccc;
}

button {
    background-color: #007BFF;
    color: white;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

.thinking {
    font-style: italic;
    color: #999;
    display: none;
    position: absolute;
    bottom: 10px;
    margin-bottom: 0;
}
</style>