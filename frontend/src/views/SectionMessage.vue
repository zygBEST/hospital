<template>
    <div>
        <!-- 卡片 -->
        <el-card>
            <!-- 面包屑 -->
            <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item :to="{ path: '/orderOperate' }">科室选择</el-breadcrumb-item>
                <el-breadcrumb-item>日期选择</el-breadcrumb-item>
                <el-breadcrumb-item>挂号</el-breadcrumb-item>
            </el-breadcrumb>

            <!-- 两边布局 -->
            <div class="head">
                <div>
                    <i class="iconfont icon-r-user1" style="margin: 5px; font-size: 26px">{{ sectionOpt }}医生列表</i>
                </div>

                <!-- 选择挂号时间 -->
                <div>
                    <i class="iconfont icon-r-paper" style="font-size: 22px">请选择你要挂号的日期：</i>
                    <ul class="dateUl">
                        <li v-for="monthDay in monthDays" :key="monthDay">
                            <el-button icon="iconfont icon-r-paper" @click="dateClick(monthDay)">{{
                                monthDay }}</el-button>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- 表格 -->
            <el-table :data="sectionData" stripe style="width: 100%" border>
                <el-table-column type="index" label="序号" width="60"></el-table-column>
                <el-table-column prop="dId" label="工号" width="80">
                </el-table-column>
                <el-table-column prop="dName" label="姓名" width="80">
                </el-table-column>
                <el-table-column prop="dGender" label="性别" width="60">
                </el-table-column>
                <el-table-column prop="dPost" label="职位" width="100">
                </el-table-column>
                <el-table-column prop="dSection" label="科室" width="100"></el-table-column>
                <el-table-column prop="dIntroduction" label="简介">
                </el-table-column>
                <el-table-column prop="dPrice" label="挂号费用/元" width="80">
                </el-table-column>
                <el-table-column prop="dAvgStar" label="评价/5分" width="80">
                </el-table-column>
                <el-table-column label="操作" width="140" v-if="clickTag">
                    <template slot-scope="scope">
                        <el-button class="iconfont icon-r-paper" style="font-size: 14px" type="warning"
                            @click="openClick(scope.row.dId, scope.row.dName, scope.row.dPrice)">
                            挂号</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
        <!-- 挂号对话框 -->
        <el-dialog title="填写挂号信息" :visible.sync="orderFormVisible">
            <el-form :model="orderForm" ref="orderForm" :rules="orderRules">
                <el-form-item label="挂号时间段" label-width="100px" prop="oTime">
                    <el-select v-model="orderForm.oTime" placeholder="请选择" no-data-text="请尝试预约明日">
                        <el-option v-for="time in times" :key="time" :label="time" :value="time">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="挂号日期" label-width="100px">
                    <el-input v-model="orderForm.orderDate" autocomplete="off" disabled></el-input>
                </el-form-item>
                <el-form-item label="医生工号" label-width="100px">
                    <el-input v-model="orderForm.dId" autocomplete="off" disabled></el-input>
                </el-form-item>
                <el-form-item label="医生姓名" label-width="100px">
                    <el-input v-model="orderForm.dName" autocomplete="off" disabled></el-input>
                </el-form-item>
                <el-form-item label="患者姓名" label-width="100px">
                    <el-input v-model="orderForm.pName" autocomplete="off" disabled></el-input>
                </el-form-item>
                <el-form-item label="患者身份证号" label-width="100px">
                    <el-input v-model="orderForm.pCard" autocomplete="off" disabled></el-input>
                </el-form-item>
                <el-form-item label="挂号费用" label-width="100px">
                    <el-input v-model="orderForm.dPrice" autocomplete="off" disabled style="width: 150px;"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click="orderFormVisible = false" style="font-size: 18px;"><i class="el-icon-close"
                        style="font-size: 20px;"></i> 取 消</el-button>
                <el-button type="primary" @click="orderSuccess('orderForm')" style="font-size: 18px;"><i
                        class="el-icon-check" style="font-size: 20px;"></i> 确 定</el-button>
            </div>
        </el-dialog>
    </div>
</template>
<script>
import jwtDecode from "jwt-decode";
import request from "@/utils/request.js";
import { getToken } from "@/utils/storage.js";
export default {
    name: "sectionMessage",
    data() {
        return {
            sectionOpt: this.$route.query.sectionOpt,
            sectionData: [],
            monthDays: [],
            clickTag: false,
            orderFormVisible: false,
            orderForm: { orderDate: "" },
            times: [],
            orderRules: {
                oTime: [
                    { required: true, message: "选择时间段", trigger: "blur" },
                ],
            },
            //挂号日期
            orderDate: "",
            //拼接时间和日期成为oId
            idTime: "",
        };
    },
    methods: {
        //打开挂号对话框触发,获取挂号时间段已剩余票数
        requestTime(id) {
            this.idTime = id + this.orderDate;
            request
                .get("patient/findOrderTime", {
                    params: {
                        arId: this.idTime,
                    },
                })
                .then((res) => {
                    const date = new Date(this.orderDate);
                    const today = new Date();
                    const isToday =
                        date.getFullYear() === today.getFullYear() &&
                        date.getMonth() === today.getMonth() &&
                        date.getDate() === today.getDate();
                    var array = [];
                    if (!this.isTimeAfterTarget("09:30") || !isToday) {
                        array.push(
                            "00:01-09:30  " + "   余号 " + res.data.data.eTOn
                        );
                    }
                    if (!this.isTimeAfterTarget("10:30") || !isToday) {
                        array.push(
                            "09:30-10:30  " + "   余号 " + res.data.data.nTOt
                        );
                    }
                    if (!this.isTimeAfterTarget("11:30") || !isToday) {
                        array.push(
                            "10:30-11:30  " + "   余号 " + res.data.data.tTOe
                        );
                    }
                    if (!this.isTimeAfterTarget("15:30") || !isToday) {
                        array.push(
                            "14:30-15:30  " + "   余号 " + res.data.data.fTOf
                        );
                    }
                    if (!this.isTimeAfterTarget("16:30") || !isToday) {
                        array.push(
                            "15:30-16:30  " + "   余号 " + res.data.data.fTOs
                        );
                    }
                    if (!this.isTimeAfterTarget("23:59") || !isToday) {
                        array.push(
                            "16:30-23:59  " + "   余号 " + res.data.data.sTOs
                        );
                    }
                    this.times = array;
                });
        },
        isTimeAfterTarget(timeString) {
            // 判断时间是否超过timeString(入参格式如：09:30)
            const currentTime = new Date();

            // 解析传入的目标时间字符串，获取小时和分钟
            const [targetHour, targetMinute] = timeString.split(":");

            // 设置要比较的时间
            const targetTime = new Date();
            targetTime.setHours(targetHour);
            targetTime.setMinutes(targetMinute);
            targetTime.setSeconds(0);

            // 比较当前时间是否超过了目标时间
            return currentTime > targetTime;
        },
        // 挂号点击确认
        orderSuccess(formName) {
            this.$refs[formName].validate((valid) => {
                if (valid) {
                    // 先提交挂号请求
                    request
                        .post("patient/addOrder", {
                            pId: this.userId,
                            dId: this.orderForm.dId,
                            oStart:
                                this.orderForm.orderDate +
                                " " +
                                this.orderForm.oTime,
                            arId: this.idTime,
                        })
                        .then((res) => {
                            console.log(res.data);
                            if (res.data.status !== 200)
                                return this.$message.error(
                                    "该时间段无剩余号源！请重新选择！"
                                );

                            // 获取挂号单号
                            const orderId = res.data.oId;

                            // 调用支付接口
                            return request.post("alipay/pay", {
                                subject: this.orderForm.pName + "挂号费",
                                tradeNo: "gh" + orderId,
                                totalAmount: this.orderForm.dPrice, // 费用
                                passbackParams: "registration"  // 挂号支付
                            });
                        })
                        .then(data => {
                            console.log(data);
                            
                            if (data.data.payUrl) {
                                // 在新窗口打开支付宝支付页面
                                window.open(data.data.payUrl, '_blank', 'width=800,height=600');
                                this.oId = data.data.tradeNo;
                                console.log("请求 oId:", this.oId);
                                // 设置轮询，确保支付完成后才继续
                                const pollInterval = 5000; // 每5秒查询一次状态
                                
                                const pollOrderStatus = setInterval(() => {
                                    request
                                        .get("order/o_state", {  
                                            params: {
                                                oId: this.oId.substring(2) // 去掉前两位
                                            },
                                        })
                                        .then((res) => {
                                            if (res.data.message === "PAID") {
                                                clearInterval(pollOrderStatus); // 停止轮询
                                                this.orderFormVisible = false;
                                                this.$message.success("挂号成功！");
                                                this.orderForm.oTime = '';
                                                this.$router.push("myOrder");
                                            }
                                        })
                                        .catch((error) => {
                                            console.error("查询订单状态出错:", error);
                                        });
                                }, pollInterval);
                            } else {
                                console.error("支付请求失败:", data);
                            }
                        })
                        .catch(error => {
                            console.error("网络错误:", error);
                        });
                } else {
                    console.log("error submit!!");
                    return false;
                }
            });
        },
        //打开挂号对话框
        openClick(id, name, price) {
            this.orderForm.dId = id;
            this.orderForm.dName = name;
            this.orderForm.pName = this.patientData.pName;
            this.orderForm.pCard = this.patientData.pCard;
            this.orderForm.dPrice = price;
            this.orderFormVisible = true;
            //请求挂号时间段
            this.requestTime(id);
        },
        //选择日期触发时间
        dateClick(date) {
            //获取挂号年月日
            const nowDate = new Date();
            let year = nowDate.getFullYear();
            this.orderForm.orderDate = year + "-" + date;
            let dateYear = year + "-" + date;
            this.orderDate = dateYear;
            request
                .get("/patient/findByTime", {
                    params: {
                        arTime: dateYear,
                        dSection: this.sectionOpt,
                    },
                })
                .then((res) => {
                    this.sectionData = res.data;
                    this.clickTag = true;
                });
        },
        //获取当天及后7天的日期星期
        nowDay(num) {
            var nowDate = new Date();
            var currentHour = nowDate.getHours();
            var currentMinute = nowDate.getMinutes();

            // 判断当前时间是否已经过了23:59
            if (
                currentHour > 23 ||
                (currentHour === 23 && currentMinute > 59)
            ) {
                num++; // 次日
            }

            nowDate.setDate(nowDate.getDate() + num);
            var month = nowDate.getMonth() + 1;
            var date = nowDate.getDate();
            if (date < 10) {
                date = "0" + date;
            }
            if (month < 10) {
                month = "0" + month;
            }
            var time = month + "-" + date;
            this.monthDays.push(time);
        },
        //请求部门医生信息
        requestSection() {
            request
                .get("patient/findDoctorBySection", {
                    params: {
                        dSection: this.$route.query.sectionOpt,
                    },
                })
                .then((res) => {
                    if (res.data.status !== 200)
                        return this.$message.error("请求数据失败");
                    this.sectionData = res.data.data.doctors;
                    console.log(res.data.data.doctors);
                });
        },
        //请求患者信息
        requestPatient() {
            request.get("patient/findPatientById", {
                params: {
                    pId: this.userId
                }
            })
                .then(res => {
                    if (res.data.status != 200)
                        return this.$message.error("获取数据失败");
                    this.patientData = res.data.data;
                    console.log(this.patientData);
                })
        }
    },
    created() {
        //获取当天的后7天
        for (var i = 0; i < 7; i++) {
            this.nowDay(i);
        }
        //按科室请求医生信息
        this.requestSection();
        //解码token信息
        const token = getToken();
        this.userId = jwtDecode(token).user_id;
        this.requestPatient();
    },
};
</script>
<style scoped lang="scss">
.dateUl li {
    display: inline;
    //margin: 5px;
    padding: 1px;
}

.dateUl {
    margin: 10px;
}

.el-breadcrumb {
    margin: 8px;
}

.head {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.el-form {
    margin-top: 0;
}
</style>