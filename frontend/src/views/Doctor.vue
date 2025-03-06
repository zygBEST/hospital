<template>
  <el-container>
    <!-- 头部 -->
    <el-header>
      <div class="head-bar">
        <div class="header-ico">
          <img src="@/assets/img/1.png" style="width: 55px;
          border-radius: 50%;
    height: 55px;
    margin-top: 7px;">
        </div>
        <div class="logo">欢迎使用医务管理系统！</div>
        <div class="time-display">
          现在是 {{ currentTime }}
        </div>
        <div class="head-right">
          <div class="head-user-con">
            <div class="user-avatar">
              <img src="../assets/8.jpg" />
            </div>
            <el-dropdown @command="handleCommand" class="user-name" trigger="click">
              <span class="el-dropdown-link">
                <span>妙手回春，<b>{{ userName }}</b>&nbsp;医生&nbsp;</span>
                <i class="el-icon-caret-bottom"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </div>
      </div>

    </el-header>
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px">
        <!-- 导航菜单 -->
        <el-menu background-color="#fafafa" active-text-color="#637ce9" :default-active="activePath">

          <el-menu-item index="doctorLayout" @click="menuClick('doctorLayout')">
            <i class="el-icon-s-home" style="font-size: 18px;"> 首页</i>
          </el-menu-item>
          <el-menu-item index="orderToday" @click="menuClick('orderToday')">
            <i class="el-icon-news" style="font-size: 18px;"> 今日挂号列表</i>
          </el-menu-item>
          <el-menu-item index="doctorOrder" @click="menuClick('doctorOrder')">
            <i class="el-icon-monitor" style="font-size: 18px;"> 历史挂号列表</i>
          </el-menu-item>
          <el-menu-item index="inBed" @click="menuClick('inBed')">
            <i class="el-icon-postcard" style="font-size: 18px;"> 住院申请管理</i>
          </el-menu-item>
          <el-menu-item index="doctorCard" @click="menuClick('doctorCard')">
            <i class="el-icon-user-solid" style="font-size: 18px;"> 个人信息查询</i>
          </el-menu-item>

        </el-menu>
      </el-aside>
      <el-main>
        <!-- 子路由入口 -->
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>
<script>
import request from "@/utils/request"; // 确保 request 已正确封装
import jwtDecode from "jwt-decode";
import { getToken, clearToken, getActivePath, setActivePath } from "@/utils/storage.js";
export default {
  name: "Doctor",
  data() {
    return {
      userName: "",
      activePath: "",
      currentTime: this.getFormattedTime(),
    };
  },
  mounted() {
    this.getUserInfo();// 页面加载时获取用户信息
    this.timer = setInterval(this.updateTime, 1000); // 每秒更新一次
  },
  methods: {
    getUserInfo() {
      const token = getToken(); // 获取 token
      if (!token) {
        return this.$message.error("请先登录！");
      }

      request.get("/getUserInfo", {
        headers: { Authorization: `Bearer ${token}` } // 在请求头中携带 token
      })
        .then(res => {
          if (res.data.status !== 200) {
            console.log(res.data);
            
            return this.$message.error("获取用户信息失败");
          }
          this.userName = res.data.data.userName; // 设置用户名
        })
        .catch(err => {
          console.error(err);
          this.$message.error("获取用户信息失败");
        });
    },
    handleCommand(command) {
      if (command === "logout") {
        this.$confirm("此操作将退出登录, 是否继续?", "提示", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        })
          .then(() => {
            clearToken();
            this.$message({
              type: "success",
              message: "退出登录成功!",
            });
            this.$router.push("login");
          })
          .catch(() => {
            this.$message({
              type: "info",
              message: "已取消",
            });
          });

      }
    },
    //token解码
    tokenDecode(token) {
      if (token !== null)
        return jwtDecode(token);
    },
    //导航栏点击事件
    menuClick(path) {
      this.activePath = path;
      setActivePath(path);
      if (this.$route.path !== "/" + path) this.$router.push(path);
      console.log(path)
    },
    //退出登录
    logout() {
      this.$confirm("此操作将退出登录, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          clearToken();
          this.$message({
            type: "success",
            message: "退出登录成功!",
          });
          this.$router.push("login");
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "已取消",
          });
        });
    },
    getFormattedTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth() + 1; // 月份从 0 开始，所以要 +1
      const day = now.getDate();
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");
      const seconds = String(now.getSeconds()).padStart(2, "0");

      return `${year}年${month}月${day}日 ${hours}:${minutes}:${seconds}`;
    },
    updateTime() {
      this.currentTime = this.getFormattedTime();
    },
  },
  beforeUnmount() {
    clearInterval(this.timer); // 组件销毁时清除定时器
  },
  created() {
    //  获取激活路径
    this.activePath = getActivePath();
    // 解码token
    this.userName = this.tokenDecode(getToken()).dName;
    console.log(this.userName);

  }
};
</script>
<style scoped lang="scss">
.title {
  cursor: pointer;
}

.el-header {
  background-color: #5b75e8;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .words {
    text-align: center;

    span {
      color: black;
    }
  }

  //border-bottom: 1px solid lightgrey;
}

.el-container {
  height: 100%;
}

.el-aside {
  margin-top: 4px;
  padding-left: 10px;
  padding-right: 10px;
  background-color: #fafafa;
  border-right: 2px solid lightgrey;
}

.el-menu {
  border: 0;
}

.el-menu-item {
  margin-top: 10px;
}

.el-menu-item.is-active {
  color: rgb(255, 255, 255) !important;
  /* 选中时的颜色 */
  border-radius: 40px;
  background-color: rgb(106, 126, 255) !important;
}

.el-menu-item:hover {
  background-color: #5887ff !important;
  /* 悬停时的背景色 */
  color: rgb(255, 255, 255) !important;
  background-color: rgb(148, 162, 255) !important;
}

.head-bar {
  position: relative;
  box-sizing: border-box;
  width: 100%;
  height: 70px;
  font-size: 22px;
  color: #fff;
  font-weight: bold;
  font-style: italic;
}

.header-ico {
  float: left;
  padding: 0 21px;
  line-height: 70px;
}

.head-bar .logo {
  float: left;
  width: 250px;
  line-height: 70px;
}

.head-right {
  float: right;
  padding-right: 50px;
}

.head-user-con {
  display: flex;
  height: 70px;
  align-items: center;
}

.btn-fullscreen {
  transform: rotate(45deg);
  margin-right: 5px;
  font-size: 24px;
}

.btn-fullscreen {
  position: relative;
  width: 30px;
  height: 30px;
  text-align: center;
  border-radius: 15px;
  cursor: pointer;
}

.btn-bell .el-icon-bell {
  color: #fff;
}

.user-name {
  margin-left: 10px;
  font-size: 18px;
}

.user-avatar {
  margin-left: 20px;
}

.user-avatar img {
  display: block;
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.el-dropdown-link {
  color: #fff;
  cursor: pointer;
}

.el-dropdown-menu__item {
  text-align: center;
}

.time-display {
  display: inline-block;
  line-height: 70px;
}
</style>