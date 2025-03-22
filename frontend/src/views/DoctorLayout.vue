<template>
  <div>

    <div class="indexPeople" style="margin-left: 10%">

      <div class="userImage">
        <i class="el-icon-user" style="font-size: 132px"></i>
      </div>

      <div class="userFont">
        <div class="spanCure">
          <span>就诊概况</span>
        </div>
        <div class="spanPeople">
          <span>今天预约挂号总人数：{{ orderPeople }}</span>
        </div>
      </div>
    </div>
    <!-- 排班信息表格 -->
    <el-card>
      <el-row>
        <el-table :data="arranges" stripe style="width: 100%;font-size: larger;" border>
          <el-table-column prop="ar_time" label="最近排班日期"></el-table-column>
        </el-table>
      </el-row>
    </el-card>

    <el-row>
      <el-col :span="24">
        <img src="@/assets/16.png" style="width: 641px;margin-left: 490px;">
      </el-col>
    </el-row>
  </div>
</template>
<script>
import request from "@/utils/request.js";
import jwtDecode from "jwt-decode";
import { getToken } from "@/utils/storage.js";
export default {
  name: "DoctorLayout",
  data() {
    return {
      userId: 1,
      orderPeople: 1,
      arranges: [], // 存储排班数据
    };
  },
  methods: {
    requestPeople() {
      request
        .get("doctor/orderPeopleByDid", {
          params: {
            dId: this.userId,
          },
        })

        .then((res) => {
          if (res.data.status !== 200)
            return this.$message.error("数据请求失败");
          this.orderPeople = res.data.data;
        });
    },
    // 获取医生排班信息
    requestSchedule() {
      request
        .get("doctor/arrangeByDid", {
          params: {
            dId: this.userId,
          },
        })
        .then((res) => {
          if (res.data.status === 200) {
            this.arranges = res.data.data;
          } else {
            this.$message.error("排班数据获取失败");
          }
        })
        .catch(() => {
          this.$message.error("服务器异常，无法获取排班数据");
        });
    },
  },
  created() {
    const token = getToken(); // 获取 token
    this.userId = jwtDecode(token).user_id;
    console.log(this.userId);
    this.requestPeople();
    this.requestSchedule(); // 获取排班信息
  },
};
</script>
<style lang="scss" scoped>
.userFont {
  height: 150px;
  width: 250px;
  float: right;
  color: white;

  .spanCure {
    font-size: 15px;
    margin-top: 60px;
    margin-bottom: 15px;
  }

  .spanPeople {
    font-size: 18px;
  }
}

.userImage {
  height: 150px;
  width: 150px;
  font-size: 130px;
  color: white;
  position: relative;
  left: 40px;
  top: 10px;
  float: left;
}

.indexPeople {
  height: 200px;
  width: 440px;
  background: #58b9ae;
  float: left;
  margin: 30px;
}
</style>