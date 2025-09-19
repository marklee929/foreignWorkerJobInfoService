package fwj.aniss.api.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import com.google.gson.Gson;
import fwj.aniss.api.common.interceptor.TokenCheckInterceptor;

//스프링의 웹 설정을 담당하는 클래스다 라고 지정해주는 어노테이션이 있다.
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

	// @Autowired
	// private CORSFilter cosFilter;

	@Bean(name = "gson")
	Gson gson() {
		Gson gson = new Gson();
		return gson;
	}

	// 인터셉터를 등록
	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		registry.addInterceptor(new TokenCheckInterceptor())
				.addPathPatterns("/**")
				.excludePathPatterns("/")
				.excludePathPatterns("/test/**")
				.excludePathPatterns("/itbong/**")
				.excludePathPatterns("/auth/doLogin")
				.excludePathPatterns("/auth/doLogout")
				.excludePathPatterns("/login/**")
				.excludePathPatterns("/board/*Form*")
				.excludePathPatterns("/board/boardList.html")
				.excludePathPatterns("/js/**")
				.excludePathPatterns("/api/telegram/**")
				.excludePathPatterns("/api/worknet/**");
	}

}