const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

// 创建客户端
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// 生成二维码
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

// 登录成功
client.on('ready', async () => {
    console.log('Client is ready!');

    // 获取群组列表
    const chats = await client.getChats();
    const groups = chats.filter(chat => chat.isGroup);
    const groupNames = groups.map(group => group.name);

    // 将群组名称保存到文件
    fs.writeFileSync('group_names.json', JSON.stringify(groupNames, null, 2));
    console.log('Group names saved to group_names.json');
});

// 启动客户端
client.initialize();