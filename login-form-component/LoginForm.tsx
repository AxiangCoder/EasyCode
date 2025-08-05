import React, { useState } from 'react';

interface LoginFormProps {
  onSubmit?: (data: { username: string; password: string; captcha: string }) => void;
  onCaptchaRefresh?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, onCaptchaRefresh }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    captcha: ''
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.(formData);
  };

  const handleCaptchaRefresh = () => {
    onCaptchaRefresh?.();
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      {/* 白色卡片容器 */}
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        
        {/* 标题 */}
        <h1 className="text-xl font-bold text-gray-800 mb-8">
          账号密码登录
        </h1>

        {/* 表单区域 */}
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* 账号输入框 */}
          <div className="relative">
            <div className="flex items-center border-b border-gray-300 pb-2">
              {/* 用户图标 */}
              <div className="w-5 h-5 mr-3">
                <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="账号"
                value={formData.username}
                onChange={handleInputChange('username')}
                className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400"
              />
            </div>
          </div>

          {/* 密码输入框 */}
          <div className="relative">
            <div className="flex items-center border-b border-gray-300 pb-2">
              {/* 密码图标 */}
              <div className="w-5 h-5 mr-3">
                <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
              </div>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="密码"
                value={formData.password}
                onChange={handleInputChange('password')}
                className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400"
              />
              {/* 密码显示/隐藏按钮 */}
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="w-5 h-5 ml-2"
              >
                {showPassword ? (
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                    <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* 验证码输入框 */}
          <div className="relative">
            <div className="flex items-center border-b border-gray-300 pb-2">
              {/* 验证码图标 */}
              <div className="w-5 h-5 mr-3">
                <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v8H4V6z" clipRule="evenodd" />
                  <path d="M6 8a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm0 3a1 1 0 011-1h4a1 1 0 110 2H7a1 1 0 01-1-1z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="请输入验证码"
                value={formData.captcha}
                onChange={handleInputChange('captcha')}
                className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400"
              />
              {/* 验证码图片 */}
              <div 
                className="ml-3 w-20 h-8 bg-gray-100 border border-gray-300 rounded cursor-pointer flex items-center justify-center"
                onClick={handleCaptchaRefresh}
              >
                <span className="text-xs text-gray-600 font-mono">70V</span>
              </div>
            </div>
          </div>

          {/* 登录按钮 */}
          <button
            type="submit"
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
          >
            登录
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginForm; 