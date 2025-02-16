import NextImage, { ImageProps } from 'next/image';

// 包装组件：剥离掉 fetchPriority 属性，避免其传递到 DOM 元素上
const CustomImage = (props: ImageProps) => {
  // 如果存在 fetchPriority，则不传递给 DOM
  const { fetchPriority, ...rest } = props as any;
  return <NextImage {...rest} />;
};

export default CustomImage; 