require('dotenv').config();
const { 
  makeCastAdd, 
  NobleEd25519Signer, 
  FarcasterNetwork,
  getHubRpcClient
} = require('@farcaster/hub-nodejs');

/**
 * 向 Farcaster 发送 cast 的函数
 * @param {string} message 需要发送的 cast 文本内容
 * @returns {Promise<any>} Farcaster cast 的响应数据
 */
async function castToFarcaster(message) {
  console.log(`向 Farcaster 发送 cast: ${message}`);
  
  // 获取 Farcaster 相关的环境变量配置
  const farcasterPrivateKey = process.env.FARCASTER_PRIVATE_KEY;
  const farcasterFID = process.env.FARCASTER_FID || "-1"; // 默认 fid 为 -1
  const hubUrl = process.env.FARCASTER_HUB_URL || "hub-grpc.farcaster.xyz:2283";

  if (!farcasterPrivateKey) {
    throw new Error("缺少 FARCASTER_PRIVATE_KEY 环境变量");
  }
  
  // 初始化 Hubble 客户端
  const hubClient = getHubRpcClient(hubUrl);
  
  // 初始化 Farcaster 签名器
  const ed25519Signer = new NobleEd25519Signer(farcasterPrivateKey);
  // 定义数据选项，指定 fid 和网络
  const dataOptions = {
    fid: parseInt(farcasterFID, 10),
    network: FarcasterNetwork.MAINNET,
  };

  try {
    // 构造 cast 消息
    const castMessage = await makeCastAdd(
      {
        text: message,
        embeds: [],
        embedsDeprecated: [],
        mentions: [],
        mentionsPositions: [],
      },
      dataOptions,
      ed25519Signer
    );

    // 提交消息到 Hubble
    const submitResult = await hubClient.submitMessage(castMessage);
    
    if (submitResult.isErr()) {
      throw new Error(`提交消息失败: ${submitResult.error}`);
    }

    return {
      success: true,
      message: castMessage,
      submitResult: submitResult.value
    };

  } catch (error) {
    console.error('Farcaster cast 错误:', error);
    throw new Error(`Farcaster cast 失败: ${error.message}`);
  } finally {
    // 关闭 Hubble 客户端连接
    hubClient.close();
  }
}

module.exports = { castToFarcaster }; 