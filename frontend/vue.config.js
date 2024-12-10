
module.exports = {
    lintOnSave: false, // 关闭eslint校验
    devServer: {
        host: "127.0.0.1",
        port: 8089,
        https: false,
        proxy: "http://127.0.0.1:5000",
        overlay: { // 关闭eslint校验
            warning: false,
            errors: false
        },
    }
}
//设置代理解决跨域问题