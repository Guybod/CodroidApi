using System;
using System.Text.Json.Nodes;
using System.Threading;
using CodroidAPI;

class Demo
{
    static string test_project_ID = "mhv9ubqz0pr69d5f";
    static void Main()
    {
        Codroid cod = new Codroid("192.168.1.136", 9001);
        cod.DEBUG = true;
        cod.Connect();
        
        // // 运行脚本
        // JsonObject vars = new JsonObject();
        // vars.Add("a", 10);
        // vars.Add("b", 20);
        // cod.RunScript("a = a+b \nprint(a)", vars: vars);
        
        // // 进入远程脚本模式
        // cod.EnterRemoteScriptMode()
        
        // // 运行项目
        // cod.RunProject(test_project_ID);
        
        // // 通过工程映射索引号运行工程
        // cod.RunProjectByIndex(1);
        
        // // 单步运行 (第一次运行时必须输入工程ID，请确保上一步运行完成再次发送单步运行)
        // cod.RunStep(test_project_ID);
        // Thread.Sleep(8000);
        // cod.RunStep();
        // Thread.Sleep(8000);
        // cod.RunStep();
        // Thread.Sleep(8000);
        // cod.RunStep();
        // Thread.Sleep(8000);

        // // 暂停工程，恢复工程，停止工程
        // cod.StopProject();
        // Thread.Sleep(8000);
        // cod.RunProject(test_project_ID);
        // Thread.Sleep(8000);
        // cod.PauseProject();
        // Thread.Sleep(8000);
        // cod.ResumeProject();
        // Thread.Sleep(8000);
        // cod.StopProject();
        // Thread.Sleep(8000);

        // // 设置断点
        // int[] lineNumber = {1, 2, 3};
        // cod.SetBreakpoint(test_project_ID, lineNumber);
        // Thread.Sleep(2000);
        // cod.AddBreakpoint(test_project_ID, lineNumber);
        // Thread.Sleep(2000);
        // // 有bug
        // // cod.RemoveBreakpoint(test_project_ID, lineNumber);
        // // Thread.Sleep(2000);
        // cod.ClearBreakpoint();
        
        // // 设置启动行
        // cod.StopProject();
        // cod.SetStartLine(3);
        // cod.RunProject(test_project_ID);
        
        // // 获取全局变量
        // cod.GetGlobalVars();
        
        // // 保存全局变量
        // cod.SetGlobalVar("Test_str", "100000", "这是一个字符串");
        // // 注意变量名规范，不能以数字开头，不能有特殊字符，不能有空
        // // cod.SetGlobalVar("111Test_str", "100000","这是一个字符串")
        // cod.SetGlobalVar("v991", 100, "这是一个数字");
        // cod.SetGlobalVar("v992", 100.1, "这是一个数字");
        // int[] a = { 1, 2, 3, 4, 5 }; 
        // double[] b = { 1.2, 3.2, 2.3, 3.4, 3, 4, 5 }; 
        // cod.SetGlobalVar("v993", a, "这是一个数组");
        // cod.SetGlobalVar("v994", b, "这是一个数组");
        // JsonObject c = new JsonObject();
        // c.Add("aaa", 100);
        // c.Add("vv", 100);
        // c.Add("cc", 100);
        // cod.SetGlobalVar("v994", c, "这是一个对象");
        
        // // 删除全局变量
        // cod.RemoveGlobalVars(new string[] { "v991", "v992", "v993" });
        
        // // 获取工程变量(必须在程序运行中才有效)
        // cod.RunProjectByIndex(0);
        // cod.GetProjectVars();
        
        // // Rs485初始化
        // cod.Rs485Init();
        
        // // Rs485清空缓存
        // cod.Rs485FlushReadBuffer();
        
        // // Rs485读
        // cod.Rs485Read(10);

        // // Rs485写
        // cod.Rs485Write(new int[] {12,34,56,78,90});
        
        cod.Disconnect();
    }
}
