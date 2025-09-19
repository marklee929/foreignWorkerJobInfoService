package fwj.aniss.api;

import org.springframework.boot.Banner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.context.annotation.PropertySource;
import org.springframework.context.annotation.PropertySources;
import org.springframework.web.WebApplicationInitializer;

@SpringBootApplication
@PropertySources({
        @PropertySource(value = "classpath:application.properties", ignoreResourceNotFound = false)
})
public class ForeignWorkerJobInfoServiceApplication extends SpringBootServletInitializer
        implements WebApplicationInitializer {

    public ForeignWorkerJobInfoServiceApplication() {
        super();
        setRegisterErrorPageFilter(false);
    }

    public static void main(String[] args) {

        SpringApplication app = new SpringApplication(ForeignWorkerJobInfoServiceApplication.class);
        app.setBannerMode(Banner.Mode.OFF);

        System.setProperty("sun.security.ssl.allowUnsafeRenegotiation", "true");

        app.run(args);
    }

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(ForeignWorkerJobInfoServiceApplication.class);
    }

}
