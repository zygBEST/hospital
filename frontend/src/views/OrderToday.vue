<template>
    <el-card>
        <el-table :data="orderData" stripe style="width: 100%" border>
            <el-table-column label="序号" type="index" width="50">
            </el-table-column>
            <el-table-column label="挂号单号" prop="oId"></el-table-column>
            <el-table-column label="患者id" prop="pId"></el-table-column>
            <el-table-column label="患者姓名" prop="pName"></el-table-column>
            <el-table-column label="医生姓名" prop="dName"></el-table-column>
            <el-table-column label="挂号时间" prop="oStart" width="200px"></el-table-column>
            <el-table-column label="挂号费用支付" prop="oGhAlipay" width="200px">
                <template slot-scope="scope">
                    <el-tag type="success" v-if="
                        scope.row.oGhAlipay === 'PAID'
                    ">已支付</el-tag>
                    <el-tag type="danger" v-if="
                        scope.row.oGhAlipay === null
                    ">未支付</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作">
                <template slot-scope="scope">
                    <el-button type="warning" style="font-size: 18px" @click="dealClick(scope.row.oId, scope.row.pId)"
                        v-if="
                            scope.row.oGhAlipay === 'PAID'
                        ">
                        <i class="el-icon-monitor" style="font-size: 18px"></i>
                        处理
                    </el-button>
                </template>
            </el-table-column>

        </el-table>
    </el-card>
</template>
<script>
import jwtDecode from "jwt-decode";
import { getToken } from "@/utils/storage.js";
import request from "@/utils/request.js";
export default {
    name: "orderToday",
    data() {
        return {
            userId: 1,
            userName: "dada",
            today: "",

            orderData: [],

        }
    },
    methods: {
        //挂号处理//页面跳转传值
        dealClick(oId, pId) {
            this.$router.push(
                {
                    path: "/dealOrder",
                    query: {
                        oId: oId,
                        pId: pId
                    }
                }
            );

        },
        //获取挂号信息
        requestOrder() {
            request.get("doctor/findOrderByToday", {
                params: {
                    dId: this.userId,
                    oStart: this.today
                }
            })
                .then(res => {
                    if (res.data.status != 200)
                        return this.$message.error("获取数据失败");
                    this.orderData = res.data.data;
                    console.log(res.data.data);
                })
        },
        //token解码
        tokenDecode(token) {
            if (token !== null)
                return jwtDecode(token);
        },
        //获取当天日期
        nowDay() {
            const nowDate = new Date();
            let date = {
                year: nowDate.getFullYear(),
                month: nowDate.getMonth() + 1,
                date: nowDate.getDate(),
            };
            if (date.date < 10) {
                date.date = "0" + date.date
            }
            if (date.month < 10) {
                date.month = "0" + date.month
            }
            this.today = date.year + "-" + date.month + "-" + date.date;

        },
    },
    created() {
        const token = getToken(); // 获取 token
        this.userId = jwtDecode(token).user_id;
        console.log(this.userId);
        //获取当天日期
        this.nowDay();
        //获取订单信息
        this.requestOrder();

    },
}
</script>