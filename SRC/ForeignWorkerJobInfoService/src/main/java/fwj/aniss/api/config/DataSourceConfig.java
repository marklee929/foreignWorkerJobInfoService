package fwj.aniss.api.config;

import java.util.HashMap;
import java.util.Map;

import javax.sql.DataSource;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.context.annotation.Primary;
import org.springframework.jdbc.datasource.LazyConnectionDataSourceProxy;

import com.zaxxer.hikari.HikariDataSource;

import lombok.RequiredArgsConstructor;

//@Configuration(proxyBeanMethods = false)
@Configuration
@RequiredArgsConstructor
public class DataSourceConfig {

    public static final String MASTER_DATASOURCE = "masterDataSource";
    public static final String SLAVE_DATASOURCE = "slaveDataSource";

    @Bean(MASTER_DATASOURCE)
    @ConfigurationProperties(prefix = "spring.datasource.master.hikari")
    public DataSource masterDataSource() {
        HikariDataSource ds = DataSourceBuilder.create()
                .type(HikariDataSource.class)
                .build();
        ds.setReadOnly(false);
        return ds;
    }

    @Bean(SLAVE_DATASOURCE)
    @ConfigurationProperties(prefix = "spring.datasource.slave.hikari")
    public DataSource slaveDataSource() {
        HikariDataSource ds = DataSourceBuilder.create()
                .type(HikariDataSource.class)
                .build();
        ds.setReadOnly(true);
        return ds;
    }

    @Bean
    @Primary
    @DependsOn({ MASTER_DATASOURCE, SLAVE_DATASOURCE })
    public DataSource routingDataSource(
            @Qualifier(MASTER_DATASOURCE) DataSource masterDataSource,
            @Qualifier(SLAVE_DATASOURCE) DataSource slaveDataSource) {

        RoutingDataSource routingDataSource = new RoutingDataSource();

        Map<Object, Object> datasourceMap = new HashMap<>();
        datasourceMap.put("master", new LazyConnectionDataSourceProxy(masterDataSource));
        datasourceMap.put("slave", new LazyConnectionDataSourceProxy(slaveDataSource));

        routingDataSource.setTargetDataSources(datasourceMap);
        routingDataSource.setDefaultTargetDataSource(masterDataSource);

        return routingDataSource;
    }

    @Bean
    @DependsOn("routingDataSource")
    public LazyConnectionDataSourceProxy dataSource(DataSource routingDataSource) {
        return new LazyConnectionDataSourceProxy(routingDataSource);
    }
}