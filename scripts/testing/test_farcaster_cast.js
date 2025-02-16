const { castToFarcaster } = require('../farcaster_cast');

async function testFarcasterCast() {
  try {
    // 这里填写你希望测试发送的 cast 内容
    const testMessage = '测试消息：Hello Farcaster!';
    console.log('开始测试发送 Farcaster cast...');
    
    const result = await castToFarcaster(testMessage);
    console.log('Farcaster cast 发送成功:', result);
    
    if (result.success) {
      console.log('消息 ID:', result.message.hash);
      console.log('提交结果:', result.submitResult);
    }
  } catch (error) {
    console.error('测试失败:', error.message);
    if (error.stack) {
      console.error('错误堆栈:', error.stack);
    }
    process.exit(1);
  }
}

testFarcasterCast();