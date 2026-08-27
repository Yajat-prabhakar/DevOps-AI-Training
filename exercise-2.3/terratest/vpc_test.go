package test

import (
	"testing"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestVpcModule(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../../exercise-1.2/modules/vpc",
		Vars: map[string]interface{}{
			"environment":          "test",
			"project":             "test-project",
			"vpc_cidr":            "10.0.0.0/16",
			"public_subnet_cidrs":  []string{"10.0.1.0/24", "10.0.2.0/24"},
			"private_subnet_cidrs": []string{"10.0.10.0/24", "10.0.20.0/24"},
			"availability_zones":   []string{"us-east-1a", "us-east-1b"},
		},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	vpcId := terraform.Output(t, terraformOptions, "vpc_id")
	assert.NotEmpty(t, vpcId)

	publicSubnetIds := terraform.OutputList(t, terraformOptions, "public_subnet_ids")
	assert.Len(t, publicSubnetIds, 2)

	privateSubnetIds := terraform.OutputList(t, terraformOptions, "private_subnet_ids")
	assert.Len(t, privateSubnetIds, 2)
}

func TestSecurityModule(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../../exercise-1.2/modules/security",
		Vars: map[string]interface{}{
			"environment": "test",
			"project":    "test-project",
			"vpc_id":     "vpc-test123",
			"vpc_cidr":   "10.0.0.0/16",
		},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	albSgId := terraform.Output(t, terraformOptions, "alb_security_group_id")
	assert.NotEmpty(t, albSgId)

	appSgId := terraform.Output(t, terraformOptions, "app_security_group_id")
	assert.NotEmpty(t, appSgId)

	dbSgId := terraform.Output(t, terraformOptions, "database_security_group_id")
	assert.NotEmpty(t, dbSgId)
}

func TestRdsModule(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../../exercise-1.2/modules/rds",
		Vars: map[string]interface{}{
			"environment":         "test",
			"project":            "test-project",
			"vpc_id":             "vpc-test123",
			"private_subnet_ids": []string{"subnet-123", "subnet-456"},
			"security_group_id":  "sg-test123",
			"instance_class":     "db.t3.micro",
			"allocated_storage":  20,
			"multi_az":          false,
			"deletion_protection": false,
		},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	dbEndpoint := terraform.Output(t, terraformOptions, "endpoint")
	assert.NotEmpty(t, dbEndpoint)

	dbPort := terraform.Output(t, terraformOptions, "port")
	assert.Equal(t, "5432", dbPort)
}

func TestSecurityGroupRules(t *testing.T) {
	t.Parallel()

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../../exercise-1.2/modules/security",
		Vars: map[string]interface{}{
			"environment": "test",
			"project":    "test-project",
			"vpc_id":     "vpc-test123",
			"vpc_cidr":   "10.0.0.0/16",
		},
	})

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	albSgId := terraform.Output(t, terraformOptions, "alb_security_group_id")
	require.NotEmpty(t, albSgId)

	appSgId := terraform.Output(t, terraformOptions, "app_security_group_id")
	require.NotEmpty(t, appSgId)

	dbSgId := terraform.Output(t, terraformOptions, "database_security_group_id")
	require.NotEmpty(t, dbSgId)
}
