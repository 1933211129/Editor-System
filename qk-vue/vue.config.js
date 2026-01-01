const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: '/xuebao/',
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  // 新增：配置 htmlWebpackPlugin 的选项
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].title = '期刊管理'; // 设置网页标题
      return args;
    });
  }
})